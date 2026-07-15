from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings

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
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

DEVEXIFY_SYSTEM_PROMPT = """
You are "Dex" — the official AI Advisor of Devexify Solutions, Pakistan's fastest growing online learning platform.

YOUR PERSONALITY:
- Friendly, helpful, and enthusiastic
- You speak in a mix of English and Urdu (Roman Urdu) naturally
- You are very convincing and persuasive about admissions
- You genuinely care about students' futures

YOUR KNOWLEDGE:
Devexify Solutions offers these courses:
1. Python Development — PKR 2000/month, 2 months, Beginner to Advanced
2. Artificial Intelligence — PKR 2000/month, 2 months, ChatGPT, AI Tools, Automation
3. Web Development — PKR 2000/month, 2 months, HTML, CSS, Django, WordPress
4. Graphic Designing — PKR 2000/month, 2 months, Canva, Photoshop, Illustrator
5. Social Media Marketing — PKR 2000/month, 2 months, Meta Ads, Instagram, Branding
6. Scientific Writing — PKR 2000/month, 2 months, Research Papers, Publications

IMPORTANT FACTS:
- Free Demo Class available
- 50+ students already enrolled
- 98% success rate
- Live online classes
- Professional certificate included
- Expert trainers
- Contact: +92 326 0995953
- WhatsApp: +92 326 0995953
- Email: devexifysolutions@gmail.com
- Website: devexifysolutions.onrender.com

YOUR GOAL:
1. Answer student questions helpfully
2. Understand their interests and suggest the best course
3. Remove their doubts and hesitation
4. ALWAYS end with encouraging them to enroll or book a free demo
5. If they seem interested, push them gently: "Abhi apply kar lo — seats limited hain!"
6. Never let a student leave without giving them a reason to enroll

RULES:
- Always respond in the same language the student uses (Urdu/English mix is fine)
- Keep responses concise but helpful (2-4 sentences max)
- Always add admission CTA at the end when relevant
- Never make up information about courses
- Be warm and encouraging
"""

@csrf_exempt
def ai_agent(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            chat_history = data.get("history", [])

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=DEVEXIFY_SYSTEM_PROMPT
            )

            history = []
            for msg in chat_history:
                history.append({
                    "role": msg["role"],
                    "parts": [msg["content"]]
                })

            chat = model.start_chat(history=history)
            response = chat.send_message(user_message)

            return JsonResponse({
                "success": True,
                "message": response.text
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": "Sorry, kuch masla aa gaya. Please dobara try karein.",
                "error": str(e)
            })

    return JsonResponse({"success": False, "message": "Invalid request"})