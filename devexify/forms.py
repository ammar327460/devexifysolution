from django import forms
from .models import Admission, StudentProfile


class AdmissionForm(forms.ModelForm):

    class Meta:
        model  = Admission
        fields = [
            "full_name", "father_name", "email", "phone",
            "whatsapp", "city", "course", "registration_type",
            "payment_method", "payment_screenshot", "message",
        ]
        widgets = {
            "full_name":    forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your full name"}),
            "father_name":  forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter father's name"}),
            "email":        forms.EmailInput(attrs={"class": "form-control", "placeholder": "example@gmail.com"}),
            "phone":        forms.TextInput(attrs={"class": "form-control", "placeholder": "03XXXXXXXXX"}),
            "whatsapp":     forms.TextInput(attrs={"class": "form-control", "placeholder": "03XXXXXXXXX"}),
            "city":         forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your city"}),
            "course":             forms.Select(attrs={"class": "form-control"}),
            "registration_type":  forms.Select(attrs={"class": "form-control"}),
            "payment_method":     forms.Select(attrs={"class": "form-control"}),
            "payment_screenshot": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Write your message..."}),
        }


class StudentProfileForm(forms.ModelForm):

    class Meta:
        model  = StudentProfile
        fields = ["full_name", "father_name", "phone", "city", "bio", "profile_pic"]
        widgets = {
            "full_name":   forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Name"}),
            "father_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Father's Name"}),
            "phone":       forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone Number"}),
            "city":        forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "bio":         forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Write a short bio..."}),
            "profile_pic": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }