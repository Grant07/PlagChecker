from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.utils import timezone
from django.utils.encoding import smart_str
from ..models import (
    Student,
    Program,
    Course,
    Assignment,
    SubmissionStatus,
    Lecturer,
    Submission,
    Preferences,
    PlagiarismReport,
    Notification
)
from ..services.utils import ACADEMIC_YEAR, HTMLToPdf
from ..helpers.authenticated_roles import lecturer_required
from datetime import datetime
from uuid import uuid4
import base64



@require_GET
@lecturer_required
def dashboard(request):
    preferences = Preferences.objects.get(user=request.user)
    courses_taught = Course.objects.filter(
        lecturers=Lecturer.objects.get(user=request.user)
    )

    programs = Program.objects.filter(course__in=courses_taught)

    students = Student.objects.filter(program__in=programs)

    assignments = Assignment.objects.filter(course__in=courses_taught).order_by(
        "-created_at"
    )

    submissions = Submission.objects.filter(assignment__in=assignments).order_by(
        "-date_submitted"
    )

    return render(
        request,
        "lecturer/dashboard.html",
        {
            "title": "e-Classroom: Lecturer Dashboard",
            "data": {
                "students": students,
                "courses_taught": courses_taught,
                "programs": programs,
                "assignments": assignments,
                "submissions": submissions,
                "preferences": preferences,
            },
        },
    )


@require_GET
@lecturer_required
def courses(request):
    preferences = Preferences.objects.get(user=request.user)
    return render(
        request,
        "lecturer/courses.html",
        {"title": "e-Classroom: Courses", "data": {"preferences": preferences}},
    )


@require_GET
@lecturer_required
def all_assignments(request):
    lecturer = Lecturer.objects.get(user=request.user)
    courses = Course.objects.filter(lecturers=lecturer)
    assignments = Assignment.objects.filter(course__in=courses)
    preferences = Preferences.objects.get(user=request.user)


    return render(
        request,
        "lecturer/assignments.html",
        {
            "title": "e-Classroom: All Assignments",
            "data": {
                "courses": courses, 
                "assignments": assignments,
                "preferences": preferences,
                "modal": {
                    "id": "new-assignment",
                }
            },
        },
    )


@require_POST
@lecturer_required
def create_assignment(request):
    try:
        assignment_course_id = request.POST.get("assignment__form__course")
        if not assignment_course_id:
            return JsonResponse({"message": "Course ID is required"}, status=400)

        assignment_title = request.POST.get("assignment__form__title")
        assignment_total = request.POST.get("assignment__form__total")
        assignment_due = request.POST.get("assignment__form__date")
        assignment_file = request.FILES.get("assignment__form__upload")
        assignment_content = request.POST.get("assignment__form__content")
        is_group_assignment = request.POST.get("assignment__form__group")
        plagiarism_checker = request.POST.get("assignment__form__plagiarism__checker")

        # Check for required fields
        if not all([assignment_title, assignment_total, assignment_due]):
            return JsonResponse({"message": "Missing Required Fields"}, status=400)

        input_date = datetime.strptime(assignment_due, "%d %b, %Y")
        input_date = input_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        input_date = timezone.make_aware(input_date)

        is_group_assignment = is_group_assignment == "true"
        plagiarism_checker = plagiarism_checker == "true"

        assignment_course = Course.objects.get(id=assignment_course_id)

        if assignment_file:
            assignment_file_data = base64.b64encode(assignment_file.read())
            assignment = Assignment.objects.create(
                title=assignment_title,
                total=int(assignment_total),
                due_date=input_date,
                file=assignment_file_data,
                is_group_assignment=is_group_assignment,
                plagiarism_checker=plagiarism_checker,
                course=assignment_course,
                lecturer=Lecturer.objects.get(user=request.user),
            )
        else:
            assignment = Assignment.objects.create(
                title=assignment_title,
                total=int(assignment_total),
                due_date=input_date,
                file=HTMLToPdf(assignment_content),
                is_group_assignment=is_group_assignment,
                plagiarism_checker=plagiarism_checker,
                course=assignment_course,
                lecturer=Lecturer.objects.get(user=request.user),
            )

        # Send notification to all students enrolled in the course
        programs = Program.objects.filter(course=assignment_course)
        if programs.exists():
            students = Student.objects.filter(program__in=programs)
            for student in students:
                Notification.objects.create(
                    recipient=student.user,
                    sender=request.user,
                    message=f"A new assignment has been created: {assignment.title}",
                    link=f"/student/assignments/{assignment_course.code}/{assignment.id}/",
                    notification_type='green'
                )
        else:
            return JsonResponse({"message": "No programs associated with the course"}, status=400)

        return JsonResponse({"message": "Assignment Created Successfully"}, status=200)

    except ValueError:
        return JsonResponse({"message": "Invalid date format"}, status=400)
    except (Assignment.DoesNotExist, Course.DoesNotExist, Lecturer.DoesNotExist) as e:
        return JsonResponse({"message": "Object does not exist"}, status=400)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)
    

@require_GET
@lecturer_required
def get_all_submissions(request):
    lecturer = Lecturer.objects.get(user=request.user)
    courses = Course.objects.filter(lecturers=lecturer)
    assignments = Assignment.objects.filter(course__in=courses)
    submissions = Submission.objects.filter(assignment__in=assignments)
    preferences = Preferences.objects.get(user=request.user)

    return render(
        request,
        "lecturer/submissions.html",
        {
            "title": "e-Classroom | All Submissions",
            "data": {
                "submissions": submissions,
                "preferences": preferences,
                "with_id": uuid4()
            },
        },
    )


@require_GET
@lecturer_required
def get_submission_with_id(request, submission_id: str):
    submission = Submission.objects.filter(id=submission_id).first()
    submission_status = SubmissionStatus.objects.get(submission=submission)
    preferences: Preferences = Preferences.objects.get(user=request.user)
    report = PlagiarismReport.objects.filter(submission=submission).first()

    if report is not None:
        # Sort the list based on the similarity_percentage in descending order
        sorted_results = sorted(report.similarity_results, key=lambda x: x['similarity_percentage'], reverse=True)

        # Slice the list to contain only the item with the highest similarity percentage
        highest_similarity_result = sorted_results[:1]

    try:
        plagiarism_percentage = round(highest_similarity_result[0]['similarity_percentage'], 2)
    except:
        plagiarism_percentage = 0

    return render(
        request,
        "lecturer/submissions.html",
        {
            "title": "e-Classroom | All Submissions",
            "data": {
                "with_id": submission_id,
                "submissions": submission,
                "preferences": preferences,
                "submission_status": submission_status,
                "plagiarism_percentage": plagiarism_percentage,
            },
        },
    )


@require_GET
@lecturer_required
def get_plagiarism_report_for_submission(request, submission_id: int):
    submission = get_object_or_404(Submission, id=submission_id)
    preferences = get_object_or_404(Preferences, user=request.user)
    report = PlagiarismReport.objects.filter(submission=submission).first()
    
    highest_similarity_submission = None  # Initialize variable to store highest similarity submission
    highest_similarity_percentage = None  # Initialize variable to store highest similarity percentage
    sources = []  # Initialize sources list

    if report is not None:
        # Sort the list based on the similarity_percentage in descending order
        sorted_results = sorted(report.similarity_results, key=lambda x: x['similarity_percentage'], reverse=True)

        # Get the highest similarity result
        highest_similarity_result = sorted_results[0]

        # Retrieve the submission instance of the highest similarity score
        highest_similarity_submission = get_object_or_404(Submission, id=highest_similarity_result['other_submission_id'])

        # Retrieve the similarity percentage of the highest similarity result
        highest_similarity_percentage = highest_similarity_result['similarity_percentage']

        # Extract other_submission_ids and their similarity percentages from all similarity results
        for result in sorted_results:
            other_submission_id = result['other_submission_id']
            similarity_percentage = result['similarity_percentage']
            submission_obj = get_object_or_404(Submission, id=other_submission_id)
            sources.append({
                'submission': submission_obj,
                'percentage': round(similarity_percentage, 2)
            })

    return render(
        request,
        "lecturer/plagiarism.html",
        {
            "title": "e-Classroom | Plagiarism Report",
            "data": {
                "with_id": submission_id,
                "submission": submission,
                "highest_similarity_submission": highest_similarity_submission if highest_similarity_submission is not None else "No Report",
                "highest_similarity_percentage": round(highest_similarity_percentage, 2) if highest_similarity_percentage is not None else "No Report",
                "sources": sources,  # Modified sources list
                "preferences": preferences,
            },
        },
    )



@lecturer_required
@require_POST
def return_assignment(request, submission_id: str):
    try:
        marks = request.POST.get("return__assignment__form__score")
        feedback = request.POST.get("return__assignment__form__feedback")

        if not (submission_id and marks):
            return JsonResponse({"message": "Missing required fields"}, status=400)

        submission = SubmissionStatus.objects.get(submission__id=submission_id)

        submission.status = "marked"
        submission.marks = int(marks)
        submission.feedback = feedback
        submission.save()

        return JsonResponse({"message": "Assignment Marked Successfully"}, status=200)
    except Submission.DoesNotExist:
        return JsonResponse({"message": "Submission not found"}, status=400)
    except ValueError:
        return JsonResponse({"message": "Invalid marks format"}, status=400)
    except Exception as err:
        return JsonResponse({"message": str(err)}, status=400)


@lecturer_required
@require_GET
def get_all_students(request):
    pass


@lecturer_required
@require_POST
def delete_assignment(request):
    assignment_id = request.POST.get("delete__model-id", "").strip()
    try:
        if not assignment_id:
            return JsonResponse({"message": "Missing Assignment ID"}, status=400)

        assignment = Assignment.objects.get(id=assignment_id)
        submission = Submission.objects.filter(assignment=assignment)
        submission_status = SubmissionStatus.objects.filter(submission__in=submission)

        if request.user.is_staff:
            # Delete all submission status
            for status in submission_status:
                status.delete()
            # Delete all submissions
            submission.delete()
            # Delete the assignment
            assignment.delete()

            return JsonResponse({"message": "Assignment Deleted successfully."}, status=200)
    except Assignment.DoesNotExist:
        return JsonResponse({"message": "Assignment does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Failed to delete assignment: {str(e)}"}, status=400)

