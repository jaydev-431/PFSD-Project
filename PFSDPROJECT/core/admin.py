from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, JobPosting, JobApplication, WorkHour, SupervisorFeedback


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role',)}),
    )


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'required_hours', 'pay_rate', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'department', 'created_at')
    search_fields = ('title', 'description', 'department')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('student__username', 'job__title')


@admin.register(WorkHour)
class WorkHourAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'date', 'hours_worked', 'status', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('student__username', 'job__title', 'task_description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SupervisorFeedback)
class SupervisorFeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'rating', 'given_by', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('student__username', 'feedback')
    readonly_fields = ('created_at',)
