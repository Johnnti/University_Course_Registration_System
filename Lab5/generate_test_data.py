import csv
import os
import random

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Sample course data
courses = [
    # Format: (course_id, name, instructor, day, start_time, end_time)
    ('MATH101', 'Math 101', 'Dr. Smith', 'Monday', '11:00', '11:50'),
    ('PHYS101', 'Physics 101', 'Dr. Johnson', 'Tuesday', '10:00', '10:50'),
    ('CHEM101', 'Chemistry 101', 'Dr. Lee', 'Wednesday', '09:00', '09:50'),
    ('ENG101', 'English 101', 'Prof. Brown', 'Thursday', '12:00', '12:50'),
    ('HIST101', 'History 101', 'Dr. Davis', 'Friday', '14:00', '14:50'),
    ('CS101', 'Computer Science 101', 'Prof. Wilson', 'Monday', '13:00', '13:50'),
    ('BIO101', 'Biology 101', 'Dr. Martinez', 'Tuesday', '14:00', '14:50'),
    ('PSY101', 'Psychology 101', 'Dr. Taylor', 'Wednesday', '11:00', '11:50'),
    ('ECON101', 'Economics 101', 'Prof. Anderson', 'Thursday', '09:00', '09:50'),
    ('ART101', 'Art History 101', 'Dr. White', 'Friday', '10:00', '10:50'),
    ('MATH102', 'Math 102', 'Dr. Smith', 'Monday', '14:00', '14:50'),
    ('PHYS102', 'Physics 102', 'Dr. Johnson', 'Tuesday', '11:00', '11:50'),
    ('CHEM102', 'Chemistry 102', 'Dr. Lee', 'Wednesday', '13:00', '13:50'),
    ('ENG102', 'English 102', 'Prof. Brown', 'Thursday', '10:00', '10:50'),
    ('HIST102', 'History 102', 'Dr. Davis', 'Friday', '09:00', '09:50'),
]

# Sample student data
students = [
    # Format: (student_id, name)
    ('S1001', 'John Doe'),
    ('S1002', 'Jane Smith'),
    ('S1003', 'Robert Johnson'),
    ('S1004', 'Emily Davis'),
    ('S1005', 'Michael Wilson'),
    ('S1006', 'Sarah Brown'),
    ('S1007', 'David Miller'),
    ('S1008', 'Jennifer Taylor'),
    ('S1009', 'James Anderson'),
    ('S1010', 'Patricia Thomas'),
]

# Generate random enrollments (each student enrolled in 3-5 courses)
enrollments = []
for student_id, _ in students:
    # Randomly select 3-5 courses for each student
    num_courses = random.randint(3, 5)
    selected_courses = random.sample([course[0] for course in courses], num_courses)
    
    for course_id in selected_courses:
        enrollments.append((student_id, course_id))

# Save courses to CSV
with open('data/courses.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['course_id', 'name', 'instructor', 'day', 'time'])
    for course in courses:
        course_id, name, instructor, day, start_time, end_time = course
        writer.writerow([course_id, name, instructor, day, f"{start_time}-{end_time}"])

# Save students to CSV
with open('data/students.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['student_id', 'name'])
    for student in students:
        writer.writerow(student)

# Save enrollments to CSV
with open('data/enrollments.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['student_id', 'course_id'])
    for enrollment in enrollments:
        writer.writerow(enrollment)

print(f"Generated {len(courses)} courses, {len(students)} students, and {len(enrollments)} enrollments.")
print("Data saved to data/courses.csv, data/students.csv, and data/enrollments.csv") 