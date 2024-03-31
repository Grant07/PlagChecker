from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse

from ..models import (
    Program,
    Course,
    Department,
    Lecturer,
    CustomUser,
    Preferences,
    Student,
)
from ..services.utils import ACADEMIC_YEAR
from ..helpers.authenticated_roles import admin_required


@require_GET
@admin_required
def program(request):
    programs = Program.objects.all()
    departments = Department.objects.all()
    return render(
        request,
        "admin/programs.html",
        {
            "title": "e-Classroom: Manage Programs",
            "admin": True,
            "data": {
                "departments": departments,
                "programs": programs,
                "modal": {
                    "id": "register-program",
                    "title": "Program",
                },
            },
        },
    )


@admin_required
@require_POST
def add_program(request):
    name = request.POST.get("program__name")
    duration = request.POST.get("program__duration")
    department = request.POST.get("program__department")

    try:
        if not (name and duration and department):
            return JsonResponse({"message": "Missing required fields"}, status=400)

        department_obj = Department.objects.get(name=department)
        program, created = Program.objects.get_or_create(
            name=name,
            duration=duration,
            department=department_obj,
        )

        if created:
            return JsonResponse({"message": "Program added successfully."}, status=200)
        else:
            return JsonResponse({"message": f"Failed! {name} already exists."}, status=400)

    except Department.DoesNotExist:
        return JsonResponse(
            {"message": f"Department '{department}' does not exist."}, status=404
        )
    except Exception as e:
        return JsonResponse({"message": f"Failed! {str(e)}"}, status=400)


@require_POST
@admin_required
def delete_program(request):
    program_id = request.POST.get("delete__model-id")

    try:
        if not program_id:
            return JsonResponse({"message": "Missing program ID"}, status=400)

        program = Program.objects.get(id=program_id)
        program.delete()
        return JsonResponse({"message": "Program deleted successfully."}, status=200)

    except Program.DoesNotExist:
        return JsonResponse({"message": "Program does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Failed to delete program: {str(e)}"}, status=400)


@require_GET
@admin_required
def dashboard(request):
    preferences = Preferences.objects.get(user=request.user)
    users = CustomUser.objects.all()
    courses = Course.objects.all()
    programs = Program.objects.all()

    return render(
        request,
        "admin/dashboard.html",
        {
            "title": "e-Classroom: Dashboard",
            "data": {
                "preferences": preferences,
                "users": {
                    "active": users.filter(is_active=True).count(),
                    "inactive": users.filter(is_active=False).count(),
                    "lecturers": users.filter(is_staff=True).count(),
                    "students": users.filter(
                        is_staff=False, is_superuser=False
                    ).count(),
                },
                "courses": courses.count(),
                "programs": programs.count(),
                "login_activity": users.exclude(last_login=None).order_by(
                    "-last_login"
                )[:5],
            },
        },
    )


@require_GET
@admin_required
def courses(request):
    programs = Program.objects.all()
    courses = Course.objects.all()
    return render(
        request,
        "admin/courses.html",
        {
            "title": "Manage Courses",
            "admin": True,
            "data": {
                "programs": programs,
                "courses": courses,
                "modal": {
                    "id": "register-course",
                    "title": "Course",
                },
            },
        },
    )


@require_POST
@admin_required
def add_course(request):
    name = request.POST.get("course__name")
    code = request.POST.get("course__code")
    semester = request.POST.get("course__semester")
    credits = request.POST.get("course__credits")
    programs = request.POST.getlist("course__programs")

    try:
        if not all([name, code, semester, credits, programs]):
            return JsonResponse({"message": "Missing required fields"}, status=400)

        # Convert credits to integer
        credits = int(credits)

        # Check if programs exist
        try:
            existing_programs = Program.objects.filter(id__in=programs)
            if len(existing_programs) != len(programs):
                return JsonResponse(
                    {"message": "One or more programs do not exist"}, status=400
                )
        except ObjectDoesNotExist:
            return JsonResponse(
                {"message": "One or more programs do not exist"}, status=400
            )

        # Create course
        course = Course.objects.create(
            name=name,
            code=code,
            semester=semester,
            credits=credits,
        )

        # Assign programs to course
        course.programs.set(existing_programs)

        return JsonResponse({"message": "Course Added Successfully"}, status=200)
    except ValueError as ve:
        return JsonResponse({"message": f"Invalid value: {ve}"}, status=400)
    except Exception as e:
        return JsonResponse({"message": f"Failed to add course: {str(e)}"}, status=400)


@require_POST
@admin_required
def delete_course(request):
    course_id = request.POST.get("delete__model-id")
    try:
        if not course_id:
            return JsonResponse({"message": "Missing course ID"}, status=400)

        course = Course.objects.get(id=course_id)
        course.delete()
        return JsonResponse({"message": "Course deleted successfully."}, status=200)
    except Course.DoesNotExist:
        return JsonResponse({"message": "Course does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Failed to delete course: {str(e)}"}, status=400)

@require_GET
@admin_required
def lectures(request):
    lecturers = Lecturer.objects.all()
    departments = Department.objects.all()
    courses = Course.objects.all()

    return render(
        request,
        "admin/users.html",
        {
            "title": "Manage Lecturers",
            "admin": True,
            "data": {
                "lecturers": lecturers,
                "departments": departments,
                "courses": courses,
                "modal": {
                    "id": "register-lecturer",
                    "title": "Lecturer",
                },
            },
        },
    )


@require_POST
@admin_required
def add_lecturer(request):
    employee_id = request.POST.get("employee__id")
    first_name = request.POST.get("first__name")
    last_name = request.POST.get("last__name")
    department_id = request.POST.get("department__id")
    courses = request.POST.getlist("lecturer__courses")

    try:
        # Check if any of the required fields is missing
        if not all([employee_id, first_name, last_name, department_id, courses]):
            return JsonResponse({"message": "Missing required fields"}, status=400)

        # Create user
        user = CustomUser.objects.create_user(
            username=employee_id,
            first_name=first_name,
            last_name=last_name,
            password="pass1234",
            is_staff=True,
            is_superuser=False,
        )

        # Create lecturer
        lecturer = Lecturer.objects.create(
            employee_id=employee_id,
            user=user,
            department=Department.objects.get(id=department_id),
        )

        # Create preferences for the lecturer
        preference = Preferences.objects.create(user=user)

        # Assign courses to lecturer
        for course_id in courses:
            course = Course.objects.get(id=course_id)
            course.lecturers.add(lecturer)

        return JsonResponse({"message": "Lecturer added successfully."}, status=200)

    except Department.DoesNotExist:
        return JsonResponse({"message": "Department does not exist"}, status=404)
    except Course.DoesNotExist:
        return JsonResponse({"message": "One or more courses do not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Failed to add lecturer: {str(e)}"}, status=400)


@admin_required
@require_POST
def delete_lecturer(request):
    user_id = request.POST.get("delete__model-id")
    try:
        if not user_id:
            return JsonResponse({"message": "Missing user ID"}, status=400)

        user = Lecturer.objects.get(id=user_id)
        user.delete()
        return JsonResponse({"message": "Lecturer deleted successfully."}, status=200)
    except Lecturer.DoesNotExist:
        return JsonResponse({"message": "Lecturer does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Failed to delete lecturer: {str(e)}"}, status=400)
