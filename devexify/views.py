from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .forms import AdmissionForm, StudentProfileForm
from .models import StudentProfile


# ============================================================
#   PUBLIC PAGES
# ============================================================

def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def courses(request):
    return render(request, "courses.html")

def contact(request):
    return render(request, "contact.html")

def team(request):
    return render(request, "team.html")


def admission(request):
    course            = request.GET.get("course", "")
    registration_type = request.GET.get("type", "")

    if request.method == "POST":
        form = AdmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "✅ Your admission has been submitted successfully! "
                "We will contact you within 24 hours after verifying your payment."
            )
            return redirect("admission")
    else:
        form = AdmissionForm()

    return render(request, "admission.html", {
        "form": form,
        "selected_course":   course,
        "registration_type": registration_type,
    })


# ============================================================
#   STUDENT PORTAL — LOGIN / LOGOUT
# ============================================================

def student_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("/admin/")
        return redirect("student_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                messages.error(request, "Admin yahan login nahi kar sakta. /admin/ use karein.")
            elif hasattr(user, "profile"):
                login(request, user)
                return redirect("student_dashboard")
            else:
                messages.error(request, "No student profile found. Contact admin.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "portal/login.html")


def student_logout(request):
    logout(request)
    return redirect("student_login")


# ============================================================
#   STUDENT PORTAL — DASHBOARD
# ============================================================

@login_required(login_url="student_login")
def student_dashboard(request):
    if request.user.is_superuser:
        return redirect("/admin/")
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        logout(request)
        messages.error(request, "No student profile found. Contact admin.")
        return redirect("student_login")
    return render(request, "portal/dashboard.html", {"profile": profile})


# ============================================================
#   STUDENT PORTAL — PROFILE
# ============================================================

@login_required(login_url="student_login")
def student_profile(request):
    if request.user.is_superuser:
        return redirect("/admin/")
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        logout(request)
        messages.error(request, "No student profile found. Contact admin.")
        return redirect("student_login")

    if request.method == "POST":
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect("student_profile")
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, "portal/profile.html", {"profile": profile, "form": form})


# ============================================================
#   STUDENT PORTAL — MY COURSE
# ============================================================

@login_required(login_url="student_login")
def my_course(request):
    if request.user.is_superuser:
        return redirect("/admin/")
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        logout(request)
        messages.error(request, "No student profile found.")
        return redirect("student_login")
    return render(request, "portal/my_course.html", {"profile": profile})