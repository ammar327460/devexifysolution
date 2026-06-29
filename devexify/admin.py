from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from .models import Admission, StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "course", "batch", "progress", "is_active"]
    list_filter   = ["course", "is_active"]
    search_fields = ["full_name", "user__username"]


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "course", "registration_type", "payment_method", "status", "created_at", "payment_image"]
    list_filter   = ["status", "course", "registration_type"]
    search_fields = ["full_name", "email", "phone"]
    actions       = ["approve_and_create_portal"]

    def approve_and_create_portal(self, request, queryset):

        for admission in queryset:

            if admission.status == "Approved":
                self.message_user(request, f"⚠️ {admission.full_name} already approved.")
                continue

            # Username banao
            base_username = admission.email.split("@")[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Random password
            password = get_random_string(10)

            # User banao
            user = User.objects.create_user(
                username=username,
                email=admission.email,
                password=password,
                first_name=admission.full_name,
            )

            # Student Profile banao
            profile = StudentProfile.objects.create(
                user=user,
                full_name=admission.full_name,
                father_name=admission.father_name,
                phone=admission.phone,
                city=admission.city,
                course=admission.course,
            )

            # Admission approve karo
            admission.student = profile
            admission.status  = "Approved"
            admission.save()

            # Portal URL — local ya production automatically
            site_url = getattr(settings, "SITE_URL", "https://devexifysolutions.onrender.com")
            portal_url = f"{site_url}/portal/login/"

            # Student ko Email bhejo
            try:
                send_mail(
                    subject=f"Devexify Solutions - Login Credentials for {admission.full_name}",
                    message=(
                        f"Assalam o Alaikum {admission.full_name},\n\n"
                        f"Aapka admission approve ho gaya hai.\n\n"
                        f"Course: {admission.course}\n"
                        f"Username: {username}\n"
                        f"Password: {password}\n"
                        f"Portal: {portal_url}\n\n"
                        f"Devexify Solutions\n"
                        f"+92 326 0995953"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admission.email],
                    html_message=f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: Arial, sans-serif; background: #f4f7ff; margin: 0; padding: 20px; }}
  .email-box {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
  .email-header {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); padding: 40px; text-align: center; color: white; }}
  .email-header h1 {{ margin: 0; font-size: 28px; }}
  .email-header p {{ margin: 10px 0 0; opacity: 0.85; }}
  .email-body {{ padding: 40px; }}
  .greeting {{ font-size: 18px; color: #111827; margin-bottom: 20px; }}
  .credentials-box {{ background: #f0f7ff; border: 2px solid #bfdbfe; border-radius: 16px; padding: 25px; margin: 25px 0; }}
  .credentials-box h3 {{ color: #1d4ed8; margin: 0 0 18px; font-size: 18px; }}
  .cred-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #dbeafe; }}
  .cred-row:last-child {{ border: none; }}
  .cred-label {{ color: #6b7280; font-size: 15px; }}
  .cred-value {{ color: #111827; font-weight: bold; font-size: 15px; }}
  .login-btn {{ display: block; background: linear-gradient(135deg,#2563eb,#1d4ed8); color: white !important; text-decoration: none; text-align: center; padding: 16px 30px; border-radius: 50px; font-size: 17px; font-weight: bold; margin: 25px 0; }}
  .warning {{ background: #fff7ed; border: 1px solid #fed7aa; border-radius: 12px; padding: 16px 20px; color: #92400e; font-size: 14px; margin-top: 20px; }}
  .email-footer {{ background: #f8fbff; padding: 25px 40px; text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; }}
</style>
</head>
<body>
<div class="email-box">
  <div class="email-header">
    <h1>Welcome to Devexify!</h1>
    <p>Your admission has been approved</p>
  </div>
  <div class="email-body">
    <p class="greeting">Assalam o Alaikum, <strong>{admission.full_name}</strong>!</p>
    <p style="color:#6b7280; line-height:28px;">
      Congratulations! Your admission for <strong>{admission.course}</strong> has been approved.
      Below are your Student Portal login credentials:
    </p>
    <div class="credentials-box">
      <h3>Your Login Details</h3>
      <div class="cred-row">
        <span class="cred-label">Portal Link</span>
        <span class="cred-value">{portal_url}</span>
      </div>
      <div class="cred-row">
        <span class="cred-label">Username</span>
        <span class="cred-value">{username}</span>
      </div>
      <div class="cred-row">
        <span class="cred-label">Password</span>
        <span class="cred-value">{password}</span>
      </div>
      <div class="cred-row">
        <span class="cred-label">Course</span>
        <span class="cred-value">{admission.course}</span>
      </div>
    </div>
    <a href="{portal_url}" class="login-btn">Login to Student Portal</a>
    <div class="warning">
      <strong>Important:</strong> Apna password change karna mat bhoolein login ke baad.
      Yeh credentials sirf aapke liye hain, kisi ke saath share mat karein.
    </div>
  </div>
  <div class="email-footer">
    <p>+92 326 0995953 | devexifysolutions@gmail.com</p>
    <p>2026 Devexify Solutions. All Rights Reserved.</p>
  </div>
</div>
</body>
</html>
                    """,
                    fail_silently=False,
                )
                self.message_user(
                    request,
                    f"✅ {admission.full_name} approved! Email sent to {admission.email} — Username: {username}",
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"✅ {admission.full_name} approved! "
                    f"⚠️ Email fail: {str(e)} — Username: {username} | Password: {password}",
                    level="warning",
                )

    approve_and_create_portal.short_description = "✅ Approve & Send Login Credentials"