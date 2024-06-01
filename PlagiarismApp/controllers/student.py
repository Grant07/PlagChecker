from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST
from django.http import Http404, JsonResponse
from ..models import (
    Student,
    Program,
    Course,
    Assignment,
    SubmissionStatus,
    Preferences,
    Submission,
    Notification
)
from ..services.utils import ACADEMIC_YEAR
from ..tasks import check_for_plagiarism
from ..helpers.authenticated_roles import student_required
import uuid
import base64

notifications = [
    {
        "name": "Mathematics",
        "department": "Math",
        "instructor": "John Doe",
        "duration": "1 hour",
    },
    {
        "name": "Physics",
        "department": "Science",
        "instructor": "Jane Smith",
        "duration": "1.5 hours",
    },
    {
        "name": "English Literature",
        "department": "Language",
        "instructor": "Alice Johnson",
        "duration": "2 hours",
    },
    {
        "name": "Computer Science",
        "department": "Computer",
        "instructor": "Bob Williams",
        "duration": "1.5 hours",
    },
    {
        "name": "History",
        "department": "Social Studies",
        "instructor": "Michael Brown",
        "duration": "2.5 hours",
    },
    {
        "name": "Chemistry",
        "department": "Science",
        "instructor": "Emily Davis",
        "duration": "1.5 hours",
    },
    {
        "name": "Biology",
        "department": "Science",
        "instructor": "David Wilson",
        "duration": "1.5 hours",
    },
]


@require_GET
@student_required
def short_courses(request):
    preferences = Preferences.objects.get(user=request.user)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)

    return render(
        request,
        "short_courses.html",
        {
            "title": "Short Courses",
            "data": {
                "short_courses": None, 
                "preferences": preferences,
                "notifications": notifications if preferences.notification else [],
                },
        },
    )


@require_GET
@student_required
def dashboard(request):
    student = Student.objects.get(user=request.user)
    preferences = Preferences.objects.get(user=request.user)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)

    try:
        program = student.program.name
    except:
        program = None

    try:
        courses = Course.objects.filter(programs=Program.objects.get(name=program))
    except:
        courses = None

    try:
        assignments = Assignment.objects.filter(course__in=courses).order_by(
            "-created_at"
        )[:5]
    except:
        assignments = None

    try:
        submissions = Submission.objects.filter(student=student)
        returned = SubmissionStatus.objects.filter(
            submission__in=submissions, status="marked"
        )[:10]

    except:
        returned = None

    return render(
        request,
        "dashboard.html",
        {
            "title": "e-Classroom | Dashboard",
            "data": {
                "academic_year": ACADEMIC_YEAR,
                "courses": courses,
                "assignments": assignments,
                "preferences": preferences,
                "returned": returned,
                "notifications": notifications if preferences.notification else None,
            },
        },
    )


@require_GET
@student_required
def my_curriculum(request):
    preferences = Preferences.objects.get(user=request.user)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    curriculum = [
        {
            "I": {
                "s1": [
                    {
                        "course_code": "CS101",
                        "course_name": "Introduction to Computer Science",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "MATH101",
                        "course_name": "Mathematics I",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "ENG101",
                        "course_name": "English Composition",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                ],
                "S2": [
                    {
                        "course_code": "CS102",
                        "course_name": "Data Structures",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "MATH102",
                        "course_name": "Mathematics II",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "HIST102",
                        "course_name": "World History",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                ],
            },
        },
        {
            "II": {
                "S1": [
                    {
                        "course_code": "PHYS101",
                        "course_name": "Physics I",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "CHEM101",
                        "course_name": "General Chemistry",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "PSYC101",
                        "course_name": "Introduction to Psychology",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                ],
                "S2": [
                    {
                        "course_code": "ART101",
                        "course_name": "Introduction to Art History",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "HIST150",
                        "course_name": "World History",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "PHYS202",
                        "course_name": "Physics II",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                ],
            },
        },
        {
            "III": {
                "S1": [
                    {
                        "course_code": "CHEM102",
                        "course_name": "Organic Chemistry",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "PSYC102",
                        "course_name": "Introduction to Psychology",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                ],
                "S2": [
                    {
                        "course_code": "ART102",
                        "course_name": "Introduction to Art History",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "HIST151",
                        "course_name": "World History",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                ],
            },
        },
        {
            "IV": {
                "S1": [
                    {
                        "course_code": "HIST103",
                        "course_name": "World History",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "HIST104",
                        "course_name": "World History",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                ],
                "S2": [
                    {
                        "course_code": "HIST105",
                        "course_name": "World History",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                    {
                        "course_code": "HIST106",
                        "course_name": "World History",
                        "course_credit": 3,
                        "course_status": "CORE",
                    },
                ],
            },
        },
    ]

    return render(
        request,
        "curriculum.html",
        {
            "title": "Curriculum",
            "data": {
                "curriculum": curriculum, 
                "preferences": preferences,
                "notifications": notifications if preferences.notification else None,
            },
        },
    )


@require_GET
@student_required
def carryover(request):
    preferences = Preferences.objects.get(user=request.user)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    
    return render(
        request,
        "carryover.html",
        {
            "title": "Carryover",
            "data": {
                "carryover": None, 
                "preferences": preferences,
                "notifications": notifications if preferences.notification else None,
            },
        },
    )


@require_GET
@student_required
def electives(request):
    preferences = Preferences.objects.get(user=request.user)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)

    return render(
        request,
        "electives.html",
        {
            "title": "Electives",
            "data": {
                "electives": None, 
                "preferences": preferences,
                "notifications": notifications if preferences.notification else None,
            },
        },
    )


@require_GET
@student_required
def get_all_assignments(request, course_code):
    assignments = Assignment.objects.filter(course=Course.objects.get(code=course_code))
    preferences = Preferences.objects.get(user=request.user)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)

    return render(
        request,
        "assignments.html",
        {
            "title": f"{course_code} Assignments",
            "data": {
                "assignments": assignments,
                "course_code": course_code,
                "preferences": preferences,
                "notifications": notifications if preferences.notification else None,
            },
        },
    )


@require_GET
@student_required
def get_assignment_uuid(request, course_code: str, assignmnet_id: uuid):
    assignment = Assignment.objects.get(id=assignmnet_id)
    submission = Submission.objects.filter(
        assignment=assignment, student=Student.objects.get(user=request.user)
    ).first()
    submission_status = SubmissionStatus.objects.filter(submission=submission).first()
    preferences = Preferences.objects.get(user=request.user)
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)

    return render(
        request,
        "assignments.html",
        {
            "title": f"{course_code}| {assignment.title}",
            "data": {
                "assignment": assignment,
                "submission": submission,
                "submission_status": submission_status,
                "course_code": course_code,
                "with_id": True,
                "preferences": preferences,
                "notifications": notifications if preferences.notification else None,
            },
        },
    )


@require_POST
@student_required
def submit_assignment(request, course_code: str, assignment_id: uuid):
    course = Course.objects.get(code=course_code)
    try:
        if request.FILES:
            assignment = Assignment.objects.get(id=assignment_id)
            upload = request.FILES.get("upload__form__input")
            if not upload:
                return JsonResponse({"message": "No file attached"}, status=400)

            upload_data = base64.b64encode(upload.read())

            student = Student.objects.get(user=request.user)

            old_submission = Submission.objects.filter(
                assignment=assignment,
                student=student,
            )

            if old_submission.exists():
                latest_submission = old_submission.first()
                old_submission.update(file=upload_data)

                if assignment.plagiarism_checker:
                    check_for_plagiarism.apply_async(args=(course.id, latest_submission.id, request.user.id), countdown=3)

                return JsonResponse(
                    {"message": "Assignment re-submitted successfully"}, status=200
                )

            submission = Submission.objects.create(
                file=upload_data,
                assignment=assignment,
                student=student,
            )

            _ = SubmissionStatus.objects.create(submission=submission)

            if assignment.plagiarism_checker:
                check_for_plagiarism.apply_async(args=(course.id, submission.id, request.user.id), countdown=5)

            return JsonResponse(
                {"message": "Assignment submitted successfully"}, status=200
            )
        else:
            return JsonResponse({"message": "No files attached"}, status=400)
    except Assignment.DoesNotExist:
        return JsonResponse({"message": "Assignment does not exist"}, status=404)
    except Student.DoesNotExist:
        return JsonResponse({"message": "Student does not exist"}, status=404)
    except Exception as err:
        return JsonResponse({"message": str(err)}, status=400)
