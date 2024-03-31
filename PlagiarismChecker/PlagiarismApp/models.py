# models.py
from json import JSONEncoder
from django.contrib.auth.models import AbstractUser
from django.db import models
from uuid import uuid4


class CustomUser(AbstractUser):
    bio = models.TextField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    image = models.BinaryField(null=True)


class Preferences(models.Model):
    THEME_OPTIONS = [
        ("light", "Light"),
        ("dark", "Dark"),
    ]

    theme = models.CharField(max_length=20, choices=THEME_OPTIONS, default="light")
    notification = models.BooleanField(default=True)
    salutation = models.CharField(max_length=100, null=True, blank=True)
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Admin(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Program(models.Model):
    name = models.CharField(max_length=100, unique=True)
    duration = models.CharField(max_length=50)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="programs"
    )

    def __str__(self):
        return self.name


class Student(models.Model):
    registration_number = models.CharField(max_length=20, unique=True)
    year_of_study = models.IntegerField(default="1")
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)


class Lecturer(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="lecturers")
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    credits = models.CharField(max_length=50)
    semester = models.CharField(max_length=50)

    programs = models.ManyToManyField(Program)
    lecturers = models.ManyToManyField(Lecturer)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(Student, related_name="groups")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="groups")

    def __str__(self):
        return self.name


class Assignment(models.Model):
    status_choices = [
        ("active", "Active"),
        ("expired", "Expired"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=100)
    content = models.TextField(null=True)
    status = models.CharField(max_length=50, choices=status_choices, default="active")
    total = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    file = models.BinaryField(null=True)
    is_group_assignment = models.BooleanField(default=False)
    plagiarism_checker = models.BooleanField(default=True)

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="assignments"
    )
    lecturer = models.ForeignKey(
        Lecturer, on_delete=models.CASCADE, related_name="assignments"
    )

    def __str__(self):
        return self.title


class GroupAssignment(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="group_assignments"
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="group_assignments"
    )


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    date_submitted = models.DateTimeField(auto_now_add=True)
    file = models.BinaryField(null=True)
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="submissions"
    )

    def __str__(self):
        return self.assignment.title


class SubmissionStatus(models.Model):
    status = models.CharField(max_length=50, default="unmarked")
    marks = models.IntegerField(null=True)
    feedback = models.TextField(default="No feedback")

    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="submission_status"
    )

    def __str__(self):
        return self.status



class PlagiarismReport(models.Model):
    similarity_results = models.JSONField(encoder=JSONEncoder)

    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="plagiarism_reports"
    )

    def __str__(self):
        return f"Plagiarism Report for Submission: {self.submission.id}"
    

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_notifications")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_notifications")
    message = models.TextField()
    link = models.CharField(max_length=100, null=True, blank=True)
    notification_type = models.CharField(choices=[('green', 'Green'), ('red', 'Red')], max_length=5)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)