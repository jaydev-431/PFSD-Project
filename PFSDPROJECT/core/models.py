from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role-based access"""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def is_student(self):
        return self.role == 'student'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class JobPosting(models.Model):
    """Job posting model for work-study positions"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    department = models.CharField(max_length=100)
    required_hours = models.IntegerField(default=0)
    pay_rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class JobApplication(models.Model):
    """Application for a job posting"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'job')

    def __str__(self):
        return f"{self.student.username} - {self.job.title}"


class WorkHour(models.Model):
    """Work hour tracking model"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_hours')
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='work_hours')
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    task_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.hours_worked}h"


class SupervisorFeedback(models.Model):
    """Supervisor feedback for student work"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    work_hour = models.ForeignKey(WorkHour, on_delete=models.CASCADE, null=True, blank=True, related_name='feedbacks')
    feedback = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    given_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedbacks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.student.username} - Rating: {self.rating}/5"
