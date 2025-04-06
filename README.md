# University Course Registration System

A Python-based course registration system for universities that allows students to register for courses, manage their schedules, and store data persistently.

## Features

- Student registration and login
- Course enrollment and dropping
- Schedule conflict prevention
- Credit limit enforcement (9-18 credits per semester)
- Class capacity limits (30 students per class)
- Persistent data storage using CSV files
- Responsive UI that works on both Mac and Windows

## Requirements

- Python 3.6 or higher
- Tkinter (usually comes with Python)

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. No additional installation is required as the system uses only standard Python libraries

## Usage

### Generating Test Data

To generate test data for testing the system:

```bash
python generate_test_data.py
```

This will create the following files in the `data` directory:
- `students.csv`: Contains student information
- `courses.csv`: Contains course information
- `enrollments.csv`: Contains enrollment records

### Running the Application

To run the main application:

```bash
python registration.py
```

### Running Tests

To run the test suite:

```bash
python test_registration.py
```

This will give you options to:
1. Run automated tests
2. Run the GUI for manual testing
3. Exit

## System Requirements

### Student Class
- Represents a student with attributes like student ID, name, and registered courses.

### Course Class
- Represents a course with attributes like course ID, name, instructor, schedule, and enrolled students.

### EnrollmentSystem Class
- Manages student-course registrations and maintains records.
- Handles data persistence using CSV files.
- Implements business rules like schedule conflict prevention and credit limits.

## Business Rules

1. Students cannot enroll in more than 6 courses (18 credits) per semester
2. Students must enroll in at least 3 courses (9 credits) per semester
3. Students cannot enroll in courses with scheduling conflicts
4. Courses cannot exceed their maximum capacity (30 students)
5. Classes are only available on weekdays (Monday-Friday)
6. Classes are only available between 8:00 AM and 5:50 PM

## Data Storage

The system stores data in CSV files:
- `students.csv`: Stores student information (student_id, name)
- `courses.csv`: Stores course details (course_id, name, instructor, day, time)
- `enrollments.csv`: Stores all enrollments (student_id, course_id)

## Testing

The system includes both automated tests and manual testing capabilities:

### Automated Tests
- Data loading verification
- Student login testing
- Course enrollment testing
- Course dropping testing
- Schedule conflict detection testing

### Manual Testing
- GUI-based testing for interactive verification

## License

This project is open source and available for educational purposes. 