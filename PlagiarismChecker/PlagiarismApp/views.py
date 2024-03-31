from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .services.utils import PlagiarismCheckerService
from .models import Student, Lecturer, Program, Course, Preferences, Submission, Assignment
from .controllers import admin, student, auth, lecturer
from .forms import CaptchaForm

import base64



@require_POST
def logout(request):
    auth_logout(request)
    return redirect("login")


def redirect_to_dashboard(request):
    if request.user.is_superuser:
        return admin.dashboard(request)
    elif request.user.is_staff:
        return lecturer.dashboard(request)
    else:
        return student.dashboard(request)


@require_POST
def validate_captcha(request):
    form = CaptchaForm(request.POST)
    try:
        if form.is_valid():
            # Captcha validation passed
            return JsonResponse({"message": "Captcha validation passed"}, status=200)
        else:
            raise
    except Exception as e:
        return JsonResponse({"message": f"{form.errors.as_text()[19:]}"}, status=400)


def profile(request):
    student_object = None
    lecturer_object = None
    preferences = Preferences.objects.get(user=request.user)

    try:
        student_object = Student.objects.get(user_id=request.user.id)
    except Student.DoesNotExist:
        try:
            lecturer_object = Lecturer.objects.get(user_id=request.user.id)
        except Lecturer.DoesNotExist:
            pass

    form = CaptchaForm()

    user = None
    if student_object:
        data = {
            "program": (
                student_object.program.name if student_object.program else None
            ),
            "yos": student_object.year_of_study if student_object.year_of_study else None,
            "preferences": preferences,
        }
    elif lecturer_object:
        data = {
            "department": (
                lecturer_object.department.name
                if lecturer_object.department
                else None
            ),
            "courses": Course.objects.filter(lecturers=lecturer_object),
            "preferences": preferences,
        }

    

    return render(
        request,
        "profile.html",
        {
            "title": "e-Classroom: Profile",
            "admin": False,
            "data": data,
            "programs": Program.objects.all(),
            "form": form,
        },
    )


@require_POST
def update_profile(request):
    try:
        rq = request.POST

        email = rq.get("email__address")
        phone = rq.get("phone__number")

        # Assuming student and lecturer objects are obtained from somewhere
        student_object = None
        lecturer_object = None

        try:
            student_object = Student.objects.get(user_id=request.user.id)
        except Student.DoesNotExist:
            try:
                lecturer_object = Lecturer.objects.get(user_id=request.user.id)
            except Lecturer.DoesNotExist:
                pass

        # Handle the case when no user object is found
        if not (student_object or lecturer_object):
            return JsonResponse({"message": "No user object found"}, status=400)

        # Process image upload
        if "image__upload-btn" in request.FILES:
            image = request.FILES["image__upload-btn"]
            image_data = base64.b64encode(image.read())
            user = student_object.user if student_object else lecturer_object.user
            user.image = image_data

        # Update user information
        user = student_object.user if student_object else lecturer_object.user
        user.phone = phone
        user.email = email
        user.save()

        if student_object:
            if rq.get("program"):
                program = get_object_or_404(Program, name=rq.get("program"))
                student_object.program = program

            student_object.save()
        elif lecturer_object:
            lecturer_object.save()

        return JsonResponse({"message": "Profile Updated Successfully. 👍🏾"}, status=200)
    except Exception as e:
        # Handle any unexpected exceptions gracefully
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=400)



@require_POST
def change_password(request):
    try:
        current_password = request.POST.get("current__password")
        new_password = request.POST.get("new__password")
        confirm_password = request.POST.get("confirm__password")

        if not (current_password and new_password and confirm_password):
            return JsonResponse({"message": "Please fill out all fields. 📝"}, status=400)

        if new_password != confirm_password:
            return JsonResponse({"message": "New password and confirm password do not match. 🙅🏽‍♂️"}, status=400)

        if not request.user.check_password(current_password):
            return JsonResponse({"message": "Incorrect Current Password. ❌"}, status=400)

        # Update the password
        request.user.set_password(new_password)
        request.user.save()
        
        return JsonResponse({"message": "Password changed successfully. 👍🏾"}, status=200)
    
    except ValueError as ve:
        return JsonResponse({"message": str(ve)}, status=400)
    
    except Exception as e:
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)


@require_POST
def change_preferences(request):
    try:
        preferences = Preferences.objects.get(user=request.user)

        dark_mode = request.POST.get("dark_mode")
        notifications = request.POST.get("notifications")
        salutations = request.POST.get("salutations")

        # Input validation
        if dark_mode not in ["true", "false"] or notifications not in ["true", "false"]:
            return JsonResponse({"message": "Invalid input for preferences."}, status=400)

        print(dark_mode, notifications, salutations)

        preferences.theme = "dark" if dark_mode == "true" else "light"
        preferences.notification = notifications == "true"
        preferences.salutation = salutations if salutations != "Please Choose" else None

        preferences.save()

        return JsonResponse({"message": "Preferences changed successfully."}, status=200)
    
    except Preferences.DoesNotExist:
        return JsonResponse({"message": "Preferences not found for this user."}, status=404)
    
    except Exception as e:
        return JsonResponse({"message": f"An error occurred: {str(e)}"}, status=500)
    

def upload_files(request):
    pgc = PlagiarismCheckerService()
    if request.method == 'POST' and request.FILES:
        pdf_files = []

        for _, file_value in request.FILES.items():
            pdf_files.append(file_value)
        
        file_paths = [pgc.save_uploaded_file(pdf_file) for pdf_file in pdf_files]
        texts = [pgc.extract_text_from_pdf(file_path) for file_path in file_paths]

        similarity_matrix = pgc.compare_texts(*texts)
        
        # Process the similarity matrix to generate similarity report
        similarity_report = []
        for i in range(len(texts)):
            for j in range(i+1, len(texts)):
                similarity_percentage = similarity_matrix[i][j] * 100
                similarity_report.append({
                    'text1_index': i + 1,
                    'text2_index': j + 1,
                    'similarity_percentage': similarity_percentage
                })
        
        return render(request, 'report.html', {'similarity_report': similarity_report})
    return render(request, 'upload.html')



@require_GET
def get_file(request):
    file_id = request.GET.get('file_id')
    file_type = request.GET.get('file_type')

    if file_id and file_type:
        if file_type == "submission":
            sub = Submission.objects.get(id=file_id)
            return JsonResponse({"file": sub.file.decode('utf-8')})
        else:
            ass = Assignment.objects.get(id=file_id)
            return JsonResponse({"file": ass.file.decode('utf-8')})