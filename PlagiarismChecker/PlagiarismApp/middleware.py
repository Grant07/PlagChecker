from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class AuthenticationEnforcementMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # Redirect authenticated users away from login and forgot password pages
            if request.path in [reverse('login'), reverse('forgot_password'), reverse('register')]:
                return redirect('home')  # Redirect to the homepage
        else:
            # Redirect unauthenticated users to the login page for all other pages except register
            if not request.path in [reverse('register'), reverse('forgot_password'), reverse('login')]:
                return redirect('login')