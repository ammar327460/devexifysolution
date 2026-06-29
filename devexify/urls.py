from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path("",           views.home,      name="home"),
    path("home/",      views.home,      name="home"),
    path("about/",     views.about,     name="about"),
    path("team/",      views.team,      name="team"),
    path("courses/",   views.courses,   name="courses"),
    path("admission/", views.admission, name="admission"),
    path("contact/",   views.contact,   name="contact"),

    # Student Portal
    path("portal/login/",     views.student_login,     name="student_login"),
    path("portal/logout/",    views.student_logout,    name="student_logout"),
    path("portal/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("portal/profile/",   views.student_profile,   name="student_profile"),
    path("portal/my-course/", views.my_course,         name="my_course"),
]