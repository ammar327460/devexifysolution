from django.db import models
from django.contrib.auth.models import User
from django.utils.html import format_html


class Admission(models.Model):

    COURSE_CHOICES = [
        ("Python Development",       "Python Development"),
        ("Artificial Intelligence",  "Artificial Intelligence"),
        ("Web Development",          "Web Development"),
        ("Graphic Designing",        "Graphic Designing"),
        ("Social Media Marketing",   "Social Media Marketing"),
        ("Scientific Writing",       "Scientific Writing"),
    ]

    REGISTRATION_CHOICES = [
        ("Course Admission", "Course Admission"),
        ("Free Demo Class",  "Free Demo Class"),
    ]

    PAYMENT_CHOICES = [
        ("Easypaisa",     "Easypaisa"),
        ("JazzCash",      "JazzCash"),
        ("Bank Transfer", "Bank Transfer"),
    ]

    STATUS_CHOICES = [
        ("Pending",  "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    full_name    = models.CharField(max_length=100)
    father_name  = models.CharField(max_length=100)
    email        = models.EmailField()
    phone        = models.CharField(max_length=20)
    whatsapp     = models.CharField(max_length=20)
    city         = models.CharField(max_length=100)

    course             = models.CharField(max_length=100, choices=COURSE_CHOICES)
    registration_type  = models.CharField(max_length=30,  choices=REGISTRATION_CHOICES)
    payment_method     = models.CharField(max_length=30,  choices=PAYMENT_CHOICES)
    payment_screenshot = models.ImageField(upload_to="payment_screenshots/", blank=True, null=True)
    message            = models.TextField(blank=True, null=True)
    transaction_id     = models.CharField(max_length=100, blank=True, null=True)

    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    student = models.OneToOneField(
        "StudentProfile",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="admission"
    )

    def payment_image(self):
        if self.payment_screenshot:
            return format_html('<img src="{}" width="120"/>', self.payment_screenshot.url)
        return "No Image"

    payment_image.short_description = "Payment Screenshot"

    def __str__(self):
        return f"{self.full_name} — {self.course}"

    class Meta:
        ordering = ["-created_at"]


class StudentProfile(models.Model):

    COURSE_CHOICES = Admission.COURSE_CHOICES

    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name   = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, blank=True)
    phone       = models.CharField(max_length=20, blank=True)
    city        = models.CharField(max_length=100, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    bio         = models.TextField(blank=True, null=True)

    course      = models.CharField(max_length=100, choices=COURSE_CHOICES)
    batch       = models.CharField(max_length=50, blank=True, default="Batch 2026")
    enrolled_on = models.DateField(auto_now_add=True)
    progress    = models.IntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    certificate = models.FileField(
    upload_to="certificates/",
    blank=True,
    null=True,
    verbose_name="Course Certificate"
    )

    def __str__(self):
        return f"{self.full_name} — {self.course}"

    class Meta:
        verbose_name        = "Student Profile"
        verbose_name_plural = "Student Profiles"
        # StudentProfile class mein is_active ke baad add karo
