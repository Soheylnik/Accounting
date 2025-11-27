import random
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from .models import OneTimePassword, Organization, User

AUTH_BACKEND = "django.contrib.auth.backends.ModelBackend"
OTP_EXPIRE_MINUTES = 5
SESSION_PENDING_VERIFICATION = "pending_phone_verification_user_id"
SESSION_DEV_CODE = "dev_last_otp_code"


def _send_otp_code(user, purpose, phone_number=None, expire_minutes=OTP_EXPIRE_MINUTES):
    phone = phone_number or user.phone_number
    code = f"{random.randint(0, 999999):06d}"
    expires_at = timezone.now() + timedelta(minutes=expire_minutes)
    OneTimePassword.objects.create(
        user=user,
        phone_number=phone,
        code=code,
        expires_at=expires_at,
        purpose=purpose,
    )
    print(f"[OTP:{purpose}] ارسال برای {phone}: {code}")
    return code


def _set_pending_verification(request, user):
    request.session[SESSION_PENDING_VERIFICATION] = str(user.id)
    request.session.modified = True


def _store_dev_code(request, code):
    request.session[SESSION_DEV_CODE] = code
    request.session.modified = True


def _consume_dev_code(request):
    return request.session.pop(SESSION_DEV_CODE, None)


class registerView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form_data": {}})

    def post(self, request):
        data = request.POST
        full_name = data.get("full_name", "").strip()
        email = data.get("email", "").strip().lower()
        phone_number = data.get("phone_number", "").strip()
        organization_name = data.get("organization_name", "").strip()
        base_currency = data.get("base_currency", "IRR").strip().upper() or "IRR"
        timezone_name = data.get("timezone", "Asia/Tehran")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        errors = []
        if not all([full_name, email, phone_number, organization_name, password, confirm_password]):
            errors.append("لطفاً همه فیلدهای الزامی را تکمیل کنید.")

        if password != confirm_password:
            errors.append("رمز عبور و تکرار آن یکسان نیستند.")

        if User.objects.filter(email=email).exists():
            errors.append("با این ایمیل قبلاً حساب ساخته شده است.")

        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            errors.append("این شماره موبایل قبلاً ثبت شده است.")

        if errors:
            return render(
                request,
                self.template_name,
                {"errors": errors, "form_data": data},
            )

        try:
            with transaction.atomic():
                organization = Organization.objects.create(
                    name=organization_name,
                    base_currency=base_currency,
                    timezone=timezone_name,
                )
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    full_name=full_name,
                    phone_number=phone_number,
                    organization=organization,
                    role=User.Roles.OWNER,
                    is_active=False,
                    phone_verified=False,
                )
        except IntegrityError:
            errors.append("خطا در ثبت اطلاعات. لطفاً دوباره تلاش کنید.")
            return render(
                request,
                self.template_name,
                {"errors": errors, "form_data": data},
            )

        _set_pending_verification(request, user)
        dev_code = _send_otp_code(user, OneTimePassword.Purposes.VERIFY_PHONE)
        _store_dev_code(request, dev_code)
        messages.success(request, "حساب ایجاد شد. کد تأیید به شماره شما ارسال شد.")
        return redirect("accounts:verify_phone")


class loginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        return self._render(request)

    def post(self, request):
        action = request.POST.get("action")
        if action == "password_login":
            return self._password_login(request)
        if action == "request_code":
            return self._request_code(request)
        if action == "verify_code":
            return self._verify_code(request)

        messages.error(request, "درخواست نامعتبر است.")
        return self._render(request)

    def _password_login(self, request):
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")
        form_data = {"identifier": identifier}

        if not identifier or not password:
            messages.error(request, "ایمیل/شماره و رمز عبور را وارد کنید.")
            return self._render(request, form_data=form_data)

        user = self._get_user_by_identifier(identifier)
        if not user or not user.check_password(password):
            messages.error(request, "اطلاعات ورود نامعتبر است.")
            return self._render(request, form_data=form_data)

        if not user.is_active:
            _set_pending_verification(request, user)
            code = _send_otp_code(user, OneTimePassword.Purposes.VERIFY_PHONE)
            _store_dev_code(request, code)
            messages.info(request, "برای فعال‌سازی حساب ابتدا شماره موبایل را تأیید کنید.")
            return redirect("accounts:verify_phone")

        if not user.phone_verified:
            _set_pending_verification(request, user)
            code = _send_otp_code(user, OneTimePassword.Purposes.VERIFY_PHONE)
            _store_dev_code(request, code)
            messages.info(request, "برای ادامه ابتدا شماره موبایل خود را تأیید کنید.")
            return redirect("accounts:verify_phone")

        login(request, user, backend=AUTH_BACKEND)
        messages.success(request, "خوش آمدید!")
        return redirect("core:dashboard_home")

    def _get_user_by_identifier(self, identifier):
        if "@" in identifier:
            return User.objects.filter(email=identifier).first()
        return User.objects.filter(phone_number=identifier).first()

    def _request_code(self, request):
        phone_number = request.POST.get("phone_number", "").strip()
        user = User.objects.filter(phone_number=phone_number, phone_verified=True, is_active=True).first()
        if not user:
            messages.error(request, "کاربری با این شماره یافت نشد.")
            return self._render(request, phone_number=phone_number)

        code = _send_otp_code(user, OneTimePassword.Purposes.LOGIN, phone_number=phone_number)
        messages.success(request, "کد ورود پیامکی ارسال شد.")
        return self._render(request, phone_number=phone_number, code_sent=True, dev_code=code)

    def _verify_code(self, request):
        phone_number = request.POST.get("phone_number", "").strip()
        code = request.POST.get("otp_code", "").strip()

        otp = (
            OneTimePassword.objects.filter(
                phone_number=phone_number,
                code=code,
                purpose=OneTimePassword.Purposes.LOGIN,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp:
            messages.error(request, "کد نامعتبر است.")
            return self._render(request, phone_number=phone_number, code_sent=True)

        if otp.is_expired:
            messages.error(request, "کد منقضی شده است. لطفاً دوباره درخواست دهید.")
            return self._render(request, phone_number=phone_number)

        user = otp.user or User.objects.filter(phone_number=phone_number, phone_verified=True).first()
        if not user:
            messages.error(request, "کاربر مرتبط با این کد یافت نشد.")
            return self._render(request)

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        login(request, user, backend=AUTH_BACKEND)
        messages.success(request, "ورود با موفقیت انجام شد.")
        return redirect("core:dashboard_home")

    def _render(self, request, **context):
        base_context = {
            "form_data": {},
            "code_sent": False,
            "phone_number": "",
            "dev_code": None,
        }
        base_context.update(context)
        return render(request, self.template_name, base_context)


class VerifyPhoneView(View):
    template_name = "accounts/verify_phone.html"

    def get(self, request):
        user = self._get_target_user(request)
        if not user:
            messages.error(request, "اطلاعات تأییدی یافت نشد. لطفاً دوباره ثبت‌نام کنید.")
            return redirect("accounts:register")

        context = {
            "phone_number": user.phone_number,
            "dev_code": request.session.get(SESSION_DEV_CODE),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = self._get_target_user(request)
        if not user:
            messages.error(request, "کاربر برای تأیید یافت نشد.")
            return redirect("accounts:register")

        action = request.POST.get("action")
        if action == "resend_code":
            code = _send_otp_code(user, OneTimePassword.Purposes.VERIFY_PHONE)
            _store_dev_code(request, code)
            messages.success(request, "کد جدید ارسال شد.")
            return render(
                request,
                self.template_name,
                {"phone_number": user.phone_number, "dev_code": code},
            )

        if action == "verify_code":
            return self._verify_code(request, user)

        messages.error(request, "درخواست نامعتبر است.")
        return redirect("accounts:verify_phone")

    def _verify_code(self, request, user):
        code = request.POST.get("otp_code", "").strip()
        otp = (
            OneTimePassword.objects.filter(
                phone_number=user.phone_number,
                code=code,
                purpose=OneTimePassword.Purposes.VERIFY_PHONE,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp:
            messages.error(request, "کد صحیح نیست.")
            return render(
                request,
                self.template_name,
                {"phone_number": user.phone_number, "dev_code": request.session.get(SESSION_DEV_CODE)},
            )

        if otp.is_expired:
            messages.error(request, "کد منقضی شده است. مجدداً درخواست دهید.")
            return render(
                request,
                self.template_name,
                {"phone_number": user.phone_number, "dev_code": request.session.get(SESSION_DEV_CODE)},
            )

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        user.phone_verified = True
        user.is_active = True
        user.save(update_fields=["phone_verified", "is_active"])

        request.session.pop(SESSION_PENDING_VERIFICATION, None)
        request.session.pop(SESSION_DEV_CODE, None)

        login(request, user, backend=AUTH_BACKEND)
        messages.success(request, "شماره موبایل تأیید و حساب فعال شد.")
        return redirect("core:dashboard_home")

    def _get_target_user(self, request):
        user_id = request.session.get(SESSION_PENDING_VERIFICATION)
        if not user_id and request.user.is_authenticated and not request.user.phone_verified:
            user_id = str(request.user.id)
            _set_pending_verification(request, request.user)
        if not user_id:
            return None
        return User.objects.filter(id=user_id).first()


class logoutView(View):
    def post(self, request):
        logout(request)
        request.session.pop(SESSION_PENDING_VERIFICATION, None)
        request.session.pop(SESSION_DEV_CODE, None)
        messages.info(request, "با موفقیت از حساب خارج شدید.")
        return redirect("core:index")