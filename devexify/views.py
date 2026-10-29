
import json
import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from google import genai
from google.genai import types

from .forms import AdmissionForm, StudentProfileForm
from .models import StudentProfile


logger = logging.getLogger(__name__)


# ============================================================
# PUBLIC PAGES
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
    course = request.GET.get("course", "")
    registration_type = request.GET.get("type", "")

    if request.method == "POST":
        form = AdmissionForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your admission has been submitted successfully! "
                "We will contact you within 24 hours after verifying your payment."
            )
            return redirect("admission")
    else:
        form = AdmissionForm()

    return render(request, "admission.html", {
        "form": form,
        "selected_course": course,
        "registration_type": registration_type,
    })


# ============================================================
# STUDENT PORTAL — LOGIN / LOGOUT
# ============================================================

def student_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("/admin/")
        return redirect("student_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            if user.is_superuser:
                messages.error(
                    request,
                    "Admin yahan login nahi kar sakta. /admin/ use karein."
                )
            elif hasattr(user, "profile"):
                login(request, user)
                return redirect("student_dashboard")
            else:
                messages.error(
                    request,
                    "No student profile found. Contact admin."
                )
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "portal/login.html")


def student_logout(request):
    logout(request)
    return redirect("student_login")


# ============================================================
# STUDENT PORTAL — DASHBOARD
# ============================================================

@login_required(login_url="student_login")
def student_dashboard(request):
    if request.user.is_superuser:
        return redirect("/admin/")

    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        logout(request)
        messages.error(
            request,
            "No student profile found. Contact admin."
        )
        return redirect("student_login")

    return render(
        request,
        "portal/dashboard.html",
        {"profile": profile}
    )


# ============================================================
# STUDENT PORTAL — PROFILE
# ============================================================

@login_required(login_url="student_login")
def student_profile(request):
    if request.user.is_superuser:
        return redirect("/admin/")

    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        logout(request)
        messages.error(
            request,
            "No student profile found. Contact admin."
        )
        return redirect("student_login")

    if request.method == "POST":
        form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Profile updated successfully!"
            )
            return redirect("student_profile")
    else:
        form = StudentProfileForm(instance=profile)

    return render(
        request,
        "portal/profile.html",
        {
            "profile": profile,
            "form": form,
        }
    )


# ============================================================
# STUDENT PORTAL — MY COURSE
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

    return render(
        request,
        "portal/my_course.html",
        {"profile": profile}
    )


# ============================================================
# DEX AI — SYSTEM PROMPT
# ============================================================

DEVEXIFY_SYSTEM_PROMPT = """
You are Dex, the official AI Advisor of Devexify Solutions,
an online learning platform in Pakistan.

YOUR PERSONALITY:
- Friendly, helpful, and enthusiastic.
- Speak naturally in the language used by the student.
- You may mix English and Roman Urdu when appropriate.
- Care about students' learning goals and future.

COURSES:
1. Python Development — PKR 2000/month, 2 months,
   Beginner to Advanced.
2. Artificial Intelligence — PKR 2000/month, 2 months,
   ChatGPT, AI Tools, Automation.
3. Web Development — PKR 2000/month, 2 months,
   HTML, CSS, Django, WordPress.
4. Graphic Designing — PKR 2000/month, 2 months,
   Canva, Photoshop, Illustrator.
5. Social Media Marketing — PKR 2000/month, 2 months,
   Meta Ads, Instagram, Branding.
6. Scientific Writing — PKR 2000/month, 2 months,
   Research Papers, Publications.

OTHER INFORMATION:
- Free demo class is available.
- Live online classes.
- Professional certificate included.
- Expert trainers.
- Contact: +92 326 0995953
- WhatsApp: +92 326 0995953
- Email: devexifysolutions@gmail.com
- Website: https://devexifysolutions.onrender.com/

RULES:
- Answer questions helpfully and accurately.
- Keep responses concise, usually 2-4 sentences.
- Recommend courses based on the student's interests.
- Encourage students to apply or book a free demo when relevant.
- Never invent course details, discounts, or guarantees.
- Be warm, respectful, and encouraging.
"""


# ============================================================
# DEX AI — CHAT API
# ============================================================

@csrf_exempt
@require_POST
def ai_agent(request):
    try:
        data = json.loads(request.body or "{}")

        if not isinstance(data, dict):
            return JsonResponse({
                "success": False,
                "message": "Invalid chat request."
            }, status=400)

        user_message = data.get("message", "")
        chat_history = data.get("history", [])

        if not isinstance(user_message, str):
            return JsonResponse({
                "success": False,
                "message": "Invalid message."
            }, status=400)

        user_message = user_message.strip()

        if not user_message:
            return JsonResponse({
                "success": False,
                "message": "Please enter a message."
            }, status=400)

        if not isinstance(chat_history, list):
            chat_history = []

        api_key = getattr(settings, "GEMINI_API_KEY", None)

        if not api_key:
            logger.error("GEMINI_API_KEY is not configured.")
            return JsonResponse({
                "success": False,
                "message": "Dex AI is not configured yet. Please try later."
            }, status=503)

        contents = []

        for msg in chat_history[-20:]:
            if not isinstance(msg, dict):
                continue

            role = msg.get("role", "")
            content = msg.get("content", "")

            if not isinstance(content, str) or not content.strip():
                continue

            if role in ("assistant", "model", "bot"):
                role = "model"
            elif role == "user":
                role = "user"
            else:
                continue

            contents.append({
                "role": role,
                "parts": [{"text": content}]
            })

        # Add the latest message after the previous history.
        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
    model="gemini-3.8-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=DEVEXIFY_SYSTEM_PROMPT,
                max_output_tokens=800,
            ),
        )

        answer = response.text

        if not answer or not answer.strip():
            logger.error("Gemini returned an empty response.")
            return JsonResponse({
                "success": False,
                "message": "Dex could not generate a reply. Please try again."
            }, status=502)

        return JsonResponse({
            "success": True,
            "message": answer.strip()
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid chat request."
        }, status=400)

    except Exception:
        logger.exception("Dex AI request failed.")
        return JsonResponse({
            "success": False,
            "message": (
                "Dex is temporarily unavailable. "
                "Please try again shortly."
            )
        }, status=502)
