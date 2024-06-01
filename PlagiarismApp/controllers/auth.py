from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.utils import IntegrityError
from ..models import CustomUser, Student, Preferences


def login(request):
    if request.method == "POST":
        loginnum = request.POST.get("loginnum")
        password = request.POST.get("password")

        # Map loginnum prefixes to dashboard URLs
        prefix_to_url = {
            "T": "dashboard",
            "E": "lecturer_dashboard",
            "A": "admin_dashboard",
        }

        # Attempt authentication
        user = authenticate(request, username=loginnum, password=password)

        if user is not None:
            # Successful authentication
            auth_login(request, user)
            redirect_url = prefix_to_url.get(loginnum[0], "dashboard")
            return redirect(redirect_url)
        else:
            # Authentication failed
            messages.error(request, "Invalid login details. Please try again.")
            return redirect("login")
    else:
        # GET request
        if request.user.is_authenticated:
            # Redirect user based on role
            if request.user.is_superuser:
                return redirect("admin_dashboard")
            elif request.user.is_staff:
                return redirect("lecturer_dashboard")
            else:
                return redirect("dashboard")
        # Render login page for unauthenticated users
        return render(request, "login.html", {"title": "e-Classroom: Login"})


def register(request):
    if request.method == "POST":
        first_name = request.POST.get("first__name")
        last_name = request.POST.get("last__name")
        registration_number = request.POST.get("registration__number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm__password")

        # Check if passwords match
        if password != confirm_password:
            return JsonResponse({"message": "Passwords Don't Match 🙅🏽‍♂️"}, status=400)

        # Add password validation here if necessary

        try:
            # Create a new user object
            user = CustomUser.objects.create_user(
                username=registration_number,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_staff=False,
                is_superuser=False,
            )

            # Create preferences
            user_preference = Preferences.objects.create(user=user)
            user_preference.save()

            # Create a new student object
            student = Student.objects.create(
                registration_number=registration_number, user=user
            )

            return JsonResponse({"message": "Registration Successful. 🫡"}, status=200)
        except IntegrityError:
            return JsonResponse(
                {"message": "Failed to register: User already exists."}, status=400
            )
        except Exception as e:
            return JsonResponse(
                {"message": f"Failed to register: {str(e)}"}, status=400
            )
    else:
        return render(request, "register.html", {"title": "e-Classroom: Registration"})


def forgot_password(request):
    return render(
        request, "forgot_password.html", {"title": "e-Classroom: Forgot Password"}
    )
