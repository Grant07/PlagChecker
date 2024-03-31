from functools import wraps
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not (request.user.is_superuser or request.user.is_staff):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Unauthorized')
            return redirect('login')
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Unauthorized')
            return redirect('login')
    return wrapper

def lecturer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff and not request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Unauthorized')
            return redirect('login')
    return wrapper
