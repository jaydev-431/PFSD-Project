from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from .models import User, JobPosting, JobApplication, WorkHour, SupervisorFeedback


def home(request):
    """Home page - redirects to login or dashboard"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        # Support login by either username or email (template may submit `email`)
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # If username not provided but email is, try to find the corresponding username
        if not username and email:
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                username = None

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email/username or password')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('login')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'student')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'registration/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'registration/register.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role
        )
        
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'registration/register.html')


@login_required
def dashboard(request):
    """Dashboard view - different for admin and student"""
    if request.user.is_admin():
        # Admin dashboard
        total_jobs = JobPosting.objects.count()
        active_jobs = JobPosting.objects.filter(is_active=True).count()
        total_students = User.objects.filter(role='student').count()
        pending_applications = JobApplication.objects.filter(status='pending').count()
        pending_hours = WorkHour.objects.filter(status='pending').count()
        
        recent_applications = JobApplication.objects.all().order_by('-applied_at')[:5]
        recent_hours = WorkHour.objects.all().order_by('-created_at')[:5]
        
        context = {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_students': total_students,
            'pending_applications': pending_applications,
            'pending_hours': pending_hours,
            'recent_applications': recent_applications,
            'recent_hours': recent_hours,
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
    else:
        # Student dashboard
        my_applications = JobApplication.objects.filter(student=request.user).order_by('-applied_at')[:5]
        my_hours = WorkHour.objects.filter(student=request.user).order_by('-date')[:5]
        
        total_hours = WorkHour.objects.filter(student=request.user, status='approved').aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
        approved_jobs = JobApplication.objects.filter(student=request.user, status='approved').count()
        
        context = {
            'my_applications': my_applications,
            'my_hours': my_hours,
            'total_hours': total_hours,
            'approved_jobs': approved_jobs,
        }
        return render(request, 'dashboard/student_dashboard.html', context)


# ============ Job Posting Views ============

@login_required
def job_list(request):
    """List all active job postings"""
    jobs = JobPosting.objects.filter(is_active=True).order_by('-created_at')
    
    # Check if user has applied
    applied_jobs = []
    if request.user.is_authenticated and not request.user.is_admin():
        applied_jobs = JobApplication.objects.filter(student=request.user).values_list('job_id', flat=True)
    
    context = {
        'jobs': jobs,
        'applied_jobs': applied_jobs,
    }
    return render(request, 'jobs/job_list.html', context)


@login_required
def job_detail(request, job_id):
    """View job details"""
    job = get_object_or_404(JobPosting, id=job_id)
    
    has_applied = False
    if not request.user.is_admin():
        has_applied = JobApplication.objects.filter(student=request.user, job=job).exists()
    
    context = {
        'job': job,
        'has_applied': has_applied,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def job_create(request):
    """Create new job posting (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'You do not have permission to create jobs')
        return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        department = request.POST.get('department')
        required_hours = request.POST.get('required_hours')
        pay_rate = request.POST.get('pay_rate')
        
        job = JobPosting.objects.create(
            title=title,
            description=description,
            department=department,
            required_hours=required_hours,
            pay_rate=pay_rate,
            created_by=request.user
        )
        
        messages.success(request, 'Job posting created successfully')
        return redirect('job_detail', job_id=job.id)
    
    return render(request, 'jobs/job_form.html')


@login_required
def job_edit(request, job_id):
    """Edit job posting (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'You do not have permission to edit jobs')
        return redirect('dashboard')
    
    job = get_object_or_404(JobPosting, id=job_id)
    
    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.department = request.POST.get('department')
        job.required_hours = request.POST.get('required_hours')
        job.pay_rate = request.POST.get('pay_rate')
        job.is_active = 'is_active' in request.POST
        job.save()
        
        messages.success(request, 'Job posting updated successfully')
        return redirect('job_detail', job_id=job.id)
    
    context = {'job': job}
    return render(request, 'jobs/job_form.html', context)


@login_required
def job_delete(request, job_id):
    """Delete job posting (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'You do not have permission to delete jobs')
        return redirect('dashboard')
    
    job = get_object_or_404(JobPosting, id=job_id)
    job.delete()
    
    messages.success(request, 'Job posting deleted successfully')
    return redirect('job_list')


@login_required
def job_apply(request, job_id):
    """Apply for a job (Student only)"""
    if request.user.is_admin():
        messages.error(request, 'Admins cannot apply for jobs')
        return redirect('job_detail', job_id=job_id)
    
    job = get_object_or_404(JobPosting, id=job_id)
    
    # Check if already applied
    if JobApplication.objects.filter(student=request.user, job=job).exists():
        messages.info(request, 'You have already applied for this job')
        return redirect('job_detail', job_id=job_id)
    
    JobApplication.objects.create(student=request.user, job=job)
    messages.success(request, 'Application submitted successfully')
    return redirect('job_list')


# ============ Application Views ============

@login_required
def application_list(request):
    """List all applications (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    applications = JobApplication.objects.all().order_by('-applied_at')
    
    context = {'applications': applications}
    return render(request, 'applications/application_list.html', context)


@login_required
def application_approve(request, app_id):
    """Approve job application (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    application = get_object_or_404(JobApplication, id=app_id)
    application.status = 'approved'
    application.save()
    
    messages.success(request, f'Application for {application.student.username} approved')
    return redirect('application_list')


@login_required
def application_reject(request, app_id):
    """Reject job application (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    application = get_object_or_404(JobApplication, id=app_id)
    application.status = 'rejected'
    application.save()
    
    messages.success(request, f'Application for {application.student.username} rejected')
    return redirect('application_list')


# ============ Work Hour Views ============

@login_required
def work_hour_log(request):
    """Log work hours (Student)"""
    if request.user.is_admin():
        messages.error(request, 'Admins cannot log work hours')
        return redirect('dashboard')
    
    # Get jobs the student is approved for
    approved_jobs = JobApplication.objects.filter(
        student=request.user, 
        status='approved'
    ).select_related('job')
    
    if request.method == 'POST':
        job_id = request.POST.get('job')
        date = request.POST.get('date')
        hours_worked = request.POST.get('hours_worked')
        task_description = request.POST.get('task_description')
        
        job = get_object_or_404(JobPosting, id=job_id)
        
        WorkHour.objects.create(
            student=request.user,
            job=job,
            date=date,
            hours_worked=hours_worked,
            task_description=task_description
        )
        
        messages.success(request, 'Work hours logged successfully')
        return redirect('work_hour_list')
    
    context = {'approved_jobs': approved_jobs}
    return render(request, 'workhours/workhour_form.html', context)


@login_required
def work_hour_list(request):
    """List work hours"""
    if request.user.is_admin():
        # Admin sees all work hours
        hours = WorkHour.objects.all().order_by('-date')
    else:
        # Student sees their own
        hours = WorkHour.objects.filter(student=request.user).order_by('-date')
    
    context = {'work_hours': hours}
    return render(request, 'workhours/workhour_list.html', context)


@login_required
def work_hour_approve(request, hour_id):
    """Approve work hours (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    hour = get_object_or_404(WorkHour, id=hour_id)
    hour.status = 'approved'
    hour.save()
    
    messages.success(request, 'Work hours approved')
    return redirect('work_hour_list')


@login_required
def work_hour_reject(request, hour_id):
    """Reject work hours (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    hour = get_object_or_404(WorkHour, id=hour_id)
    hour.status = 'rejected'
    hour.save()
    
    messages.success(request, 'Work hours rejected')
    return redirect('work_hour_list')


# ============ Feedback Views ============

@login_required
def feedback_list(request):
    """List feedbacks - all for admin, own for student"""
    if request.user.is_admin():
        feedbacks = SupervisorFeedback.objects.all().order_by('-created_at')
    else:
        feedbacks = SupervisorFeedback.objects.filter(student=request.user).order_by('-created_at')
    
    context = {'feedbacks': feedbacks}
    return render(request, 'feedbacks/feedback_list.html', context)


@login_required
def feedback_create(request, student_id):
    """Give feedback to a student (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    student = get_object_or_404(User, id=student_id, role='student')
    
    # Get student's work hours
    work_hours = WorkHour.objects.filter(student=student, status='approved')
    
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        rating = request.POST.get('rating')
        work_hour_id = request.POST.get('work_hour')
        
        work_hour = None
        if work_hour_id:
            work_hour = get_object_or_404(WorkHour, id=work_hour_id)
        
        SupervisorFeedback.objects.create(
            student=student,
            work_hour=work_hour,
            feedback=feedback_text,
            rating=rating,
            given_by=request.user
        )
        
        messages.success(request, 'Feedback given successfully')
        return redirect('feedback_list')
    
    context = {'student': student, 'work_hours': work_hours}
    return render(request, 'feedbacks/feedback_form.html', context)


# ============ Student Management (Admin) ============

@login_required
def student_list(request):
    """List all students (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    students = User.objects.filter(role='student').order_by('username')
    
    context = {'students': students}
    return render(request, 'students/student_list.html', context)


@login_required
def student_detail(request, student_id):
    """View student details (Admin only)"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    student = get_object_or_404(User, id=student_id, role='student')
    
    applications = JobApplication.objects.filter(student=student).order_by('-applied_at')
    work_hours = WorkHour.objects.filter(student=student).order_by('-date')
    feedbacks = SupervisorFeedback.objects.filter(student=student).order_by('-created_at')
    
    total_hours = work_hours.filter(status='approved').aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
    
    context = {
        'student': student,
        'applications': applications,
        'work_hours': work_hours,
        'feedbacks': feedbacks,
        'total_hours': total_hours,
    }
    return render(request, 'students/student_detail.html', context)
