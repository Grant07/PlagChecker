# urls.py

from django.urls import re_path, path
from django.views.generic import RedirectView
from . import views



urlpatterns = [
    path('', views.redirect_to_dashboard, name='home'),
    path('', views.redirect_to_dashboard, name='dashboard'),

    # Auth URLs
    path('login/', views.auth.login, name='login'),
    path('register/', views.auth.register, name='register'),
    path('forgot-password/', views.auth.forgot_password, name='forgot_password'),
    path('logout/', views.logout, name='logout'),

    # Admin URLs
    path('admin/', views.admin.dashboard, name='admin_dashboard'),
    path('admin/dashboard/', views.admin.dashboard, name='admin_dashboard'),
    path('admin/programs/', views.admin.program, name='programs'),
    path('admin/programs/add_program/', views.admin.add_program, name="add_program"),
    path('admin/programs/delete_program/', views.admin.delete_program, name='delete_program'),
    path('admin/courses/', views.admin.courses, name='courses'),
    path('admin/courses/add_course/', views.admin.add_course, name="add_course"),
    path('admin/courses/delete_course/', views.admin.delete_course, name="delete_course"),
    path('admin/lecturers/', views.admin.lectures, name='lecturers'),
    path('admin/lecturers/add_lecturer/', views.admin.add_lecturer, name="add_lecturer"),
    path('admin/lecturers/delete_lecturer/', views.admin.delete_lecturer, name="delete_lecturer"),

    # Lecturer URLs
    path('lecturer/', views.lecturer.dashboard, name='lecturer_dashboard'),
    path('lecturer/dashboard/', views.lecturer.dashboard, name='lecturer_dashboard'),
    path('lecturer/assignments/', views.lecturer.all_assignments, name='lecturer_assignments'),
    path('lecturer/assignments/create_assignment/', views.lecturer.create_assignment, name='create_assignment'),
    path('lecturer/assignments/submissions/', views.lecturer.get_all_submissions, name='get_all_submissions'),
    path('lecturer/assignments/submissions/<str:submission_id>/', views.lecturer.get_submission_with_id, name='get_submission_with_id'),
    path('lecturer/assignments/submissions/<str:submission_id>/report/', views.lecturer.get_plagiarism_report_for_submission, name='get_plagiarism_report_for_submission'),
    path('lecturer/assignments/submissions/<str:submission_id>/return/', views.lecturer.return_assignment, name='return_assignment'),
    path('lecturer/courses/all/students/', views.lecturer.get_all_students, name='get_all_students'),

    # Student URLs
    path('student/', views.student.dashboard, name='student_dashboard'),
    path('student/dashboard/', views.student.dashboard, name='dashboard'),
    path('student/curriculum/', views.student.my_curriculum, name='curriculum'),
    path('student/carryover/', views.student.carryover, name='carryover'),
    path('student/electives/', views.student.electives, name='electives'),
    path('student/short_courses/', views.student.short_courses, name='short_courses'),
    path('student/assignments/<str:course_code>/', views.student.get_all_assignments, name='all_assignments'),
    path('student/assignments/<str:course_code>/<uuid:assignmnet_id>/', views.student.get_assignment_uuid, name='get_assignment_uuid'),
    path('student/assignments/<str:course_code>/<uuid:assignment_id>/submit/', views.student.submit_assignment, name='submit_assignment'),

    # Profile URLs
    path('account/profile/', views.profile, name='profile'),
    path('account/profile/update_profile/', views.update_profile, name='update_profile'),
    path('account/profile/change_password/', views.change_password, name='change_password'),
    path('account/profile/change_preferences/', views.change_preferences, name="change_preferences"),

    # API URLs
    path('api/v2/get_file', views.get_file, name='get_file'),


    # Captcha URL
    re_path(r'validate/captcha/?', views.validate_captcha, name='captcha'),

    re_path(r'test_pgc/?', views.upload_files, name='upload_files'),

    
]
