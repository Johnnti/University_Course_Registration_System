import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import datetime

# --------------------------
# Helper Functions for Time
# --------------------------
def time_to_minutes(time_str):
    """Converts 'HH:MM' to total minutes from midnight."""
    hours, minutes = map(int, time_str.split(":"))
    return hours * 60 + minutes

def is_time_conflict(schedule1, schedule2):
    """
    Checks if two schedules conflict.
    Each schedule is a tuple: (day, start_time, end_time)
    Conflict exists if days are equal and time intervals overlap.
    """
    day1, start1, end1 = schedule1
    day2, start2, end2 = schedule2
    if day1 != day2:
        return False
    s1, e1 = time_to_minutes(start1), time_to_minutes(end1)
    s2, e2 = time_to_minutes(start2), time_to_minutes(end2)
    return s1 < e2 and s2 < e1

def is_within_allowed_time(schedule):
    """
    Check that the course's schedule is within allowed hours:
    Weekdays only and between 8:00 and 17:50.
    """
    day, start, end = schedule
    # Allowed days: Monday to Friday
    if day not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        return False
    start_minutes = time_to_minutes(start)
    end_minutes = time_to_minutes(end)
    if start_minutes < time_to_minutes("08:00") or end_minutes > time_to_minutes("17:50"):
        return False
    return True

# --------------------------
# Data Model Classes
# --------------------------
class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        # Store course IDs that the student is enrolled in.
        self.registered_courses = set()

class Course:
    def __init__(self, course_id, name, instructor, schedule, max_students=30, credits=3):
        self.course_id = course_id
        self.name = name
        self.instructor = instructor
        self.schedule = schedule  # Tuple: (day, start, end)
        self.enrolled_students = set()
        self.max_students = max_students
        self.credits = credits
        
        if not is_within_allowed_time(schedule):
            raise ValueError(f"Course {course_id} schedule {schedule} is out of allowed hours or on a weekend.")

class EnrollmentSystem:
    def __init__(self):
        # Dictionaries to store students and courses.
        self.students = {}  # key: student_id, value: Student object
        self.courses = {}   # key: course_id, value: Course object
        
        # Create data directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Load data from CSV files
        self.load_data()
        
        # If no courses exist, create hypothetical courses
        if not self.courses:
            self.courses = create_hypothetical_courses()
            self.save_courses()
    
    def load_data(self):
        """Load student and course data from CSV files."""
        # Load students
        if os.path.exists('data/students.csv'):
            with open('data/students.csv', 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        student_id, name = row[0], row[1]
                        self.students[student_id] = Student(student_id, name)
        
        # Load courses
        if os.path.exists('data/courses.csv'):
            with open('data/courses.csv', 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 5:
                        course_id, name, instructor, day, time = row[0], row[1], row[2], row[3], row[4]
                        start_time, end_time = time.split('-')
                        schedule = (day, start_time, end_time)
                        try:
                            self.courses[course_id] = Course(course_id, name, instructor, schedule)
                        except ValueError as e:
                            print(f"Error loading course {course_id}: {e}")
        
        # Load enrollments
        if os.path.exists('data/enrollments.csv'):
            with open('data/enrollments.csv', 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        student_id, course_id = row[0], row[1]
                        if student_id in self.students and course_id in self.courses:
                            student = self.students[student_id]
                            course = self.courses[course_id]
                            student.registered_courses.add(course_id)
                            course.enrolled_students.add(student_id)
    
    def save_data(self):
        """Save all data to CSV files."""
        self.save_students()
        self.save_courses()
        self.save_enrollments()
    
    def save_students(self):
        """Save student data to CSV file."""
        with open('data/students.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['student_id', 'name'])
            for student in self.students.values():
                writer.writerow([student.student_id, student.name])
    
    def save_courses(self):
        """Save course data to CSV file."""
        with open('data/courses.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['course_id', 'name', 'instructor', 'day', 'time'])
            for course in self.courses.values():
                day, start, end = course.schedule
                writer.writerow([course.course_id, course.name, course.instructor, day, f"{start}-{end}"])
    
    def save_enrollments(self):
        """Save enrollment data to CSV file."""
        with open('data/enrollments.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['student_id', 'course_id'])
            for student in self.students.values():
                for course_id in student.registered_courses:
                    writer.writerow([student.student_id, course_id])
    
    def add_student(self, student_id, name):
        """Add a new student to the system."""
        if student_id in self.students:
            raise ValueError("Student ID already exists.")
        self.students[student_id] = Student(student_id, name)
        self.save_students()
    
    def enroll_student(self, student_id, course_id):
        """Enroll a student in a course."""
        # Ensure student and course exist.
        if student_id not in self.students:
            raise ValueError("Student does not exist.")
        if course_id not in self.courses:
            raise ValueError("Course does not exist.")
        
        student = self.students[student_id]
        course = self.courses[course_id]
        
        # Check if already enrolled.
        if course_id in student.registered_courses:
            raise ValueError("Student is already enrolled in this course.")
        
        # Check course capacity.
        if len(course.enrolled_students) >= course.max_students:
            raise ValueError("Course is already full.")
        
        # Check scheduling conflicts with already registered courses.
        for cid in student.registered_courses:
            other_course = self.courses[cid]
            if is_time_conflict(course.schedule, other_course.schedule):
                raise ValueError(f"Scheduling conflict with {other_course.course_id} ({other_course.name}).")
        
        # Check credit limit: maximum 6 courses (6 x 3 = 18 credits)
        if len(student.registered_courses) >= 6:
            raise ValueError("Enrolling in this course would exceed the maximum allowed credits (18).")
        
        # Enroll the student.
        student.registered_courses.add(course_id)
        course.enrolled_students.add(student_id)
        self.save_enrollments()
    
    def drop_course(self, student_id, course_id):
        """Drop a student from a course."""
        if student_id not in self.students:
            raise ValueError("Student does not exist.")
        student = self.students[student_id]
        if course_id not in student.registered_courses:
            raise ValueError("Student is not enrolled in the specified course.")
        
        # Check credit limit: dropping would leave fewer than 3 courses (9 credits).
        if len(student.registered_courses) <= 3:
            raise ValueError("Dropping this course would result in fewer than the minimum required credits (9).")
        
        # Proceed to drop.
        student.registered_courses.remove(course_id)
        course = self.courses[course_id]
        course.enrolled_students.remove(student_id)
        self.save_enrollments()
    
    def get_student_courses(self, student_id):
        """Get all courses a student is enrolled in."""
        if student_id not in self.students:
            raise ValueError("Student does not exist.")
        return [self.courses[cid] for cid in self.students[student_id].registered_courses]
    
    def get_available_courses(self):
        """Get all available courses."""
        return list(self.courses.values())

def create_hypothetical_courses():
    """
    Creates a dictionary of hypothetical courses.
    Each course is created with a schedule within allowed hours and on weekdays.
    """
    courses = {}
    try:
        courses['MATH101'] = Course('MATH101', 'Math 101', 'Dr. Smith', schedule=('Monday', '11:00', '11:50'))
        courses['PHYS101'] = Course('PHYS101', 'Physics 101', 'Dr. Johnson', schedule=('Tuesday', '10:00', '10:50'))
        courses['CHEM101'] = Course('CHEM101', 'Chemistry 101', 'Dr. Lee', schedule=('Wednesday', '09:00', '09:50'))
        courses['ENG101']  = Course('ENG101', 'English 101', 'Prof. Brown', schedule=('Thursday', '12:00', '12:50'))
        courses['HIST101'] = Course('HIST101', 'History 101', 'Dr. Davis', schedule=('Friday', '14:00', '14:50'))
        courses['CS101']   = Course('CS101', 'Computer Science 101', 'Prof. Wilson', schedule=('Monday', '13:00', '13:50'))
        courses['BIO101']  = Course('BIO101', 'Biology 101', 'Dr. Martinez', schedule=('Tuesday', '14:00', '14:50'))
        courses['PSY101']  = Course('PSY101', 'Psychology 101', 'Dr. Taylor', schedule=('Wednesday', '11:00', '11:50'))
        courses['ECON101'] = Course('ECON101', 'Economics 101', 'Prof. Anderson', schedule=('Thursday', '09:00', '09:50'))
        courses['ART101']  = Course('ART101', 'Art History 101', 'Dr. White', schedule=('Friday', '10:00', '10:50'))
    except ValueError as ve:
        print("Error creating course:", ve)
    return courses

# --------------------------
# Tkinter UI Application
# --------------------------
class RegistrationApp:
    def __init__(self, root, enrollment_system):
        self.root = root
        self.root.title("University Course Registration System")
        self.system = enrollment_system
        self.current_student_id = None
        
        # Configure the root window to be responsive
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main container
        self.main_container = tk.Frame(self.root)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Create frames for different screens
        self.welcome_frame = tk.Frame(self.main_container)
        self.login_frame = tk.Frame(self.main_container)
        self.registration_frame = tk.Frame(self.main_container)
        self.course_frame = tk.Frame(self.main_container)
        
        # Configure all frames to be responsive
        for frame in [self.welcome_frame, self.login_frame, self.registration_frame, self.course_frame]:
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
        
        # Initialize UI components
        self.setup_welcome_screen()
        self.setup_login_screen()
        self.setup_registration_screen()
        self.setup_course_screen()
        
        # Show welcome screen initially
        self.show_welcome_screen()
    
    def setup_welcome_screen(self):
        """Setup the welcome screen with a welcome message and login button"""
        # Create a container for the welcome content
        welcome_container = tk.Frame(self.welcome_frame)
        welcome_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        welcome_container.grid_rowconfigure(0, weight=1)
        welcome_container.grid_columnconfigure(0, weight=1)
        
        # Welcome message
        welcome_label = tk.Label(
            welcome_container, 
            text="Welcome to the University Course Registration System",
            font=("Arial", 18, "bold"),
            wraplength=500
        )
        welcome_label.grid(row=0, column=0, pady=(0, 20))
        
        # Description
        description = tk.Label(
            welcome_container,
            text="This system allows you to register for courses, manage your schedule, and track your enrollment status.",
            font=("Arial", 12),
            wraplength=500
        )
        description.grid(row=1, column=0, pady=(0, 30))
        
        # Login button
        login_btn = ttk.Button(
            welcome_container,
            text="Login / Register",
            command=self.show_login_screen,
            style="Accent.TButton"
        )
        login_btn.grid(row=2, column=0, pady=10)
    
    def setup_login_screen(self):
        """Setup the login screen with student ID and name fields"""
        # Create a container for the login content
        login_container = tk.Frame(self.login_frame)
        login_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        login_container.grid_rowconfigure(0, weight=1)
        login_container.grid_columnconfigure(0, weight=1)
        
        # Login form container
        form_frame = tk.Frame(login_container)
        form_frame.grid(row=0, column=0, sticky="nsew")
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = tk.Label(
            form_frame,
            text="Student Login",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Student ID field
        tk.Label(form_frame, text="Student ID:", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.student_id_entry = ttk.Entry(form_frame, width=30)
        self.student_id_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Name field
        tk.Label(form_frame, text="Name:", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Buttons container
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Login button
        self.login_btn = ttk.Button(
            btn_frame,
            text="Login",
            command=self.login_student
        )
        self.login_btn.grid(row=0, column=0, padx=5)
        
        # Register button
        self.register_btn = ttk.Button(
            btn_frame,
            text="Register",
            command=self.register_student
        )
        self.register_btn.grid(row=0, column=1, padx=5)
        
        # Back button
        back_btn = ttk.Button(
            btn_frame,
            text="Back",
            command=self.show_welcome_screen
        )
        back_btn.grid(row=0, column=2, padx=5)
        
        # Status message
        self.login_status = tk.Label(login_container, text="", fg="red", wraplength=400)
        self.login_status.grid(row=1, column=0, pady=10)
    
    def setup_registration_screen(self):
        """Setup the registration screen for new students"""
        # Create a container for the registration content
        reg_container = tk.Frame(self.registration_frame)
        reg_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        reg_container.grid_rowconfigure(0, weight=1)
        reg_container.grid_columnconfigure(0, weight=1)
        
        # Registration form container
        form_frame = tk.Frame(reg_container)
        form_frame.grid(row=0, column=0, sticky="nsew")
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = tk.Label(
            form_frame,
            text="New Student Registration",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Student ID field
        tk.Label(form_frame, text="Student ID:", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.reg_student_id_entry = ttk.Entry(form_frame, width=30)
        self.reg_student_id_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Name field
        tk.Label(form_frame, text="Name:", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.reg_name_entry = ttk.Entry(form_frame, width=30)
        self.reg_name_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Buttons container
        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Register button
        self.reg_btn = ttk.Button(
            btn_frame,
            text="Register",
            command=self.complete_registration
        )
        self.reg_btn.grid(row=0, column=0, padx=5)
        
        # Back button
        back_btn = ttk.Button(
            btn_frame,
            text="Back",
            command=self.show_login_screen
        )
        back_btn.grid(row=0, column=1, padx=5)
        
        # Status message
        self.reg_status = tk.Label(reg_container, text="", fg="red", wraplength=400)
        self.reg_status.grid(row=1, column=0, pady=10)
    
    def setup_course_screen(self):
        """Setup the course registration screen"""
        # Create a container for the course content
        course_container = tk.Frame(self.course_frame)
        course_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        course_container.grid_rowconfigure(0, weight=1)
        course_container.grid_columnconfigure(0, weight=1)
        
        # Header with student info
        self.student_info_frame = tk.Frame(course_container)
        self.student_info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.student_info_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(self.student_info_frame, text="Student:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.student_name_label = tk.Label(self.student_info_frame, text="", font=("Arial", 11))
        self.student_name_label.grid(row=0, column=1, sticky=tk.W)
        
        # Logout button
        logout_btn = ttk.Button(self.student_info_frame, text="Logout", command=self.logout)
        logout_btn.grid(row=0, column=2, padx=5)
        
        # Main content area
        content_frame = tk.Frame(course_container)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Available Courses List
        available_frame = tk.LabelFrame(content_frame, text="Available Courses")
        available_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        available_frame.grid_rowconfigure(1, weight=1)
        available_frame.grid_columnconfigure(0, weight=1)
        
        self.available_listbox = tk.Listbox(available_frame, width=50, height=10)
        self.available_listbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add scrollbar to available courses
        available_scrollbar = ttk.Scrollbar(available_frame, orient="vertical", command=self.available_listbox.yview)
        available_scrollbar.grid(row=1, column=1, sticky="ns")
        self.available_listbox.config(yscrollcommand=available_scrollbar.set)
        
        self.enroll_btn = ttk.Button(available_frame, text="Enroll Selected Course", command=self.enroll_course)
        self.enroll_btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Registered Courses List
        registered_frame = tk.LabelFrame(content_frame, text="Your Registered Courses")
        registered_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        registered_frame.grid_rowconfigure(1, weight=1)
        registered_frame.grid_columnconfigure(0, weight=1)
        
        self.registered_listbox = tk.Listbox(registered_frame, width=50, height=10)
        self.registered_listbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add scrollbar to registered courses
        registered_scrollbar = ttk.Scrollbar(registered_frame, orient="vertical", command=self.registered_listbox.yview)
        registered_scrollbar.grid(row=1, column=1, sticky="ns")
        self.registered_listbox.config(yscrollcommand=registered_scrollbar.set)
        
        self.drop_btn = ttk.Button(registered_frame, text="Drop Selected Course", command=self.drop_course)
        self.drop_btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Status message
        self.course_status = tk.Label(course_container, text="", fg="red", wraplength=700)
        self.course_status.grid(row=2, column=0, pady=10)
    
    def show_welcome_screen(self):
        """Show the welcome screen and hide others"""
        self.welcome_frame.grid(row=0, column=0, sticky="nsew")
        self.login_frame.grid_remove()
        self.registration_frame.grid_remove()
        self.course_frame.grid_remove()
    
    def show_login_screen(self):
        """Show the login screen and hide others"""
        self.welcome_frame.grid_remove()
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        self.registration_frame.grid_remove()
        self.course_frame.grid_remove()
        
        # Clear any previous error messages
        self.login_status.config(text="")
    
    def show_registration_screen(self):
        """Show the registration screen and hide others"""
        self.welcome_frame.grid_remove()
        self.login_frame.grid_remove()
        self.registration_frame.grid(row=0, column=0, sticky="nsew")
        self.course_frame.grid_remove()
        
        # Clear any previous error messages
        self.reg_status.config(text="")
    
    def show_course_screen(self):
        """Show the course screen and hide others"""
        self.welcome_frame.grid_remove()
        self.login_frame.grid_remove()
        self.registration_frame.grid_remove()
        self.course_frame.grid(row=0, column=0, sticky="nsew")
        
        # Update student info
        if self.current_student_id and self.current_student_id in self.system.students:
            student = self.system.students[self.current_student_id]
            self.student_name_label.config(text=f"{student.name} ({student.student_id})")
        
        # Update course lists
        self.update_course_lists()
    
    def login_student(self):
        """Handle student login"""
        student_id = self.student_id_entry.get().strip()
        name = self.name_entry.get().strip()
        
        if not student_id or not name:
            self.login_status.config(text="Please enter both Student ID and Name.")
            return
        
        # Check if student exists
        if student_id in self.system.students:
            student = self.system.students[student_id]
            if student.name == name:
                self.current_student_id = student_id
                self.show_course_screen()
            else:
                self.login_status.config(text="Invalid name for this Student ID.")
        else:
            self.login_status.config(text="Student ID not found. Please register first.")
    
    def register_student(self):
        """Handle student registration from login screen"""
        student_id = self.student_id_entry.get().strip()
        name = self.name_entry.get().strip()
        
        if not student_id or not name:
            self.login_status.config(text="Please enter both Student ID and Name.")
            return
        
        # Check if student already exists
        if student_id in self.system.students:
            self.login_status.config(text="Student ID already exists. Please login instead.")
            return
        
        # Pre-fill registration form
        self.reg_student_id_entry.delete(0, tk.END)
        self.reg_student_id_entry.insert(0, student_id)
        self.reg_name_entry.delete(0, tk.END)
        self.reg_name_entry.insert(0, name)
        
        # Show registration screen
        self.show_registration_screen()
    
    def complete_registration(self):
        """Complete the registration process"""
        student_id = self.reg_student_id_entry.get().strip()
        name = self.reg_name_entry.get().strip()
        
        if not student_id or not name:
            self.reg_status.config(text="Please enter both Student ID and Name.")
            return
        
        try:
            self.system.add_student(student_id, name)
            self.current_student_id = student_id
            self.show_course_screen()
        except ValueError as e:
            self.reg_status.config(text=str(e))
    
    def logout(self):
        """Handle student logout"""
        self.current_student_id = None
        self.show_welcome_screen()
    
    def update_course_lists(self):
        """Update the available and registered course lists"""
        # Update available courses listbox
        self.available_listbox.delete(0, tk.END)
        for course in self.system.get_available_courses():
            info = f"{course.course_id}: {course.name} ({course.schedule[0]} {course.schedule[1]}-{course.schedule[2]}) | Enrolled: {len(course.enrolled_students)}/{course.max_students}"
            self.available_listbox.insert(tk.END, info)
        
        # Update registered courses listbox
        self.registered_listbox.delete(0, tk.END)
        try:
            student_courses = self.system.get_student_courses(self.current_student_id)
            for course in student_courses:
                info = f"{course.course_id}: {course.name} ({course.schedule[0]} {course.schedule[1]}-{course.schedule[2]})"
                self.registered_listbox.insert(tk.END, info)
        except ValueError as e:
            self.course_status.config(text=str(e))
    
    def enroll_course(self):
        """Handle course enrollment"""
        selection = self.available_listbox.curselection()
        if not selection:
            self.course_status.config(text="Please select a course to enroll.")
            return
        
        # Extract course_id from the selected line
        course_line = self.available_listbox.get(selection[0])
        course_id = course_line.split(":")[0]
        
        try:
            self.system.enroll_student(self.current_student_id, course_id)
            self.course_status.config(text=f"Enrolled in course {course_id} successfully!", fg="green")
            self.update_course_lists()
        except ValueError as e:
            self.course_status.config(text=str(e), fg="red")
    
    def drop_course(self):
        """Handle course dropping"""
        selection = self.registered_listbox.curselection()
        if not selection:
            self.course_status.config(text="Please select a course to drop.")
            return
        
        course_line = self.registered_listbox.get(selection[0])
        course_id = course_line.split(":")[0]
        
        try:
            self.system.drop_course(self.current_student_id, course_id)
            self.course_status.config(text=f"Dropped course {course_id} successfully!", fg="green")
            self.update_course_lists()
        except ValueError as e:
            self.course_status.config(text=str(e), fg="red")

# --------------------------
# Main Execution
# --------------------------
if __name__ == "__main__":
    # Create the enrollment system (with pre-populated hypothetical courses).
    enrollment_system = EnrollmentSystem()

    # Create the main Tkinter window.
    root = tk.Tk()
    
    # Configure styles
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Arial", 11, "bold"))
    
    # Create the application
    app = RegistrationApp(root, enrollment_system)
    
    # Start the main loop
    root.mainloop()