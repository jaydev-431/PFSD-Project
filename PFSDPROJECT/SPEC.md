# Work-Study Program Management System - Specification

## 1. Project Overview

**Project Name:** Work-Study Management System  
**Project Type:** Web Application (Django)  
**Core Functionality:** A system to manage part-time job postings, work-hour tracking, and supervisor feedback for students in work-study programs.  
**Target Users:** Admin (program managers) and Students

---

## 2. Technology Stack

- **Framework:** Django 4.x
- **Python:** 3.x
- **Database:** SQLite (default, can be changed to PostgreSQL)
- **Frontend:** HTML, CSS (Bootstrap 5), JavaScript
- **Authentication:** Django built-in authentication

---

## 3. User Roles

### Admin
- Can create, edit, and delete job postings
- Can view all students and their work records
- Can add supervisor feedback for students
- Can manage all work-hour submissions

### Student
- Can view available job postings
- Can log work hours
- Can view their own work history
- Can view supervisor feedback

---

## 4. Core Features

### 4.1 Job Postings
- Create job posting (title, description, department, hours required, pay rate)
- List all active job postings
- Edit/delete job postings (Admin only)
- Apply for jobs (Student)

### 4.2 Work-Hour Tracking
- Log work hours (date, hours worked, task description)
- View personal work history
- View all submissions (Admin)
- Approve/reject work hours (Admin)

### 4.3 Supervisor Feedback
- Add feedback for student work (Admin)
- View feedback history (Student)
- Rating system (1-5 stars)

---

## 5. Data Models

### User
- Extends Django's AbstractUser
- Role: 'admin' or 'student'

### JobPosting
- title: CharField
- description: TextField
- department: CharField
- required_hours: IntegerField
- pay_rate: DecimalField
- is_active: BooleanField
- created_by: ForeignKey(User)
- created_at: DateTimeField

### JobApplication
- student: ForeignKey(User)
- job: ForeignKey(JobPosting)
- status: CharField (pending/approved/rejected)
- applied_at: DateTimeField

### WorkHour
- student: ForeignKey(User)
- job: ForeignKey(JobPosting)
- date: DateField
- hours_worked: DecimalField
- task_description: TextField
- status: CharField (pending/approved/rejected)
- created_at: DateTimeField

### SupervisorFeedback
- student: ForeignKey(User)
- work_hour: ForeignKey(WorkHour, nullable=True)
- feedback: TextField
- rating: IntegerField (1-5)
- given_by: ForeignKey(User)
- created_at: DateTimeField

---

## 6. UI/UX Design

### Color Scheme
- Primary: #2C3E50 (Dark Blue-Gray)
- Secondary: #3498DB (Blue)
- Accent: #27AE60 (Green)
- Background: #ECF0F1 (Light Gray)
- Card Background: #FFFFFF

### Layout
- Responsive navbar with role-based menu
- Dashboard with cards for quick stats
- Tables with sorting and filtering
- Forms with validation feedback

---

## 7. Pages & Routes

### Public
- `/` - Home/Login page

### Student
- `/student/dashboard/` - Student dashboard
- `/student/jobs/` - View job postings
- `/student/jobs/<id>/` - Job details
- `/student/jobs/<id>/apply/` - Apply for job
- `/student/hours/log/` - Log work hours
- `/student/hours/` - View work history
- `/student/feedback/` - View feedback

### Admin
- `/admin/dashboard/` - Admin dashboard
- `/admin/jobs/` - Manage job postings
- `/admin/jobs/create/` - Create job
- `/admin/jobs/<id>/edit/` - Edit job
- `/admin/jobs/<id>/delete/` - Delete job
- `/admin/applications/` - View applications
- `/admin/hours/` - Review work hours
- `/admin/hours/<id>/approve/` - Approve hours
- `/admin/feedback/<student_id>/` - Give feedback

---

## 8. Acceptance Criteria

1. ✅ User can register as Admin or Student
2. ✅ Admin can create, edit, delete job postings
3. ✅ Student can view and apply for jobs
4. ✅ Student can log work hours
5. ✅ Admin can approve/reject work hours
6. ✅ Admin can give feedback with ratings
7. ✅ Student can view their feedback
8. ✅ Role-based access control works correctly
9. ✅ Responsive design works on mobile and desktop
