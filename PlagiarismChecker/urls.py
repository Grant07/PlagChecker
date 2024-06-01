"""
URL configuration for PlagiarismChecker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include, re_path
from django.views.generic import TemplateView
from PlagiarismApp import urls

urlpatterns = [
    # path('old-admin-not-setup-url-should-totally-not-be-here/', admin.site.urls),
    path('', include(urls)),
    path('captcha/', include('captcha.urls')), #capthca urls
    re_path(r'^.*$', TemplateView.as_view(template_name='404.html'), name='404'),
]
