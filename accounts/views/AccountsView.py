from accounts.serializers.AccountSerializer import (
    SignUpSerializer,
    SignInSerializer,
    PasswordResetSerializer,
    ChangePasswordSerializer,
    UserSerializer,
)
from rest_framework.serializers import ValidationError
from accounts.models.UserModel import User, PassResetToken, dk, token as tk
from accounts.models.OTPModel import OTPToken
from core.signals import Send_Mail, Send_Sms
from core import settings
from exizprint.models.services import NotificationToken, Notification
from exizprint.serializers.service_serializer import NotificationSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import DateTimeField
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework import status
from rest_framework.reverse import reverse

from knox.models import AuthToken
from post_office.models import EmailTemplate
from phonenumbers import parse as validate_phone
from pyisemail import is_email as validate_email

from django.contrib.auth.signals import user_logged_in

from django.utils import timezone
from django.db.models import Q

# ------------------------------------------------------------#
# -------- Implement Logout User Later In Next Commit --------#
# ------------------------------------------------------------#


class Base:
    def get_context(self):
        return {"request": self.request, "format": self.format_kwarg, "view": self}

    def get_token_ttl(self):
        return settings.REST_KNOX["TOKEN_TTL"]

    def get_token_limit_per_user(self):
        return settings.REST_KNOX["TOKEN_LIMIT_PER_USER"]

    def get_expiry_datetime_format(self):
        return settings.REST_KNOX["EXPIRY_DATETIME_FORMAT"]

    def format_expiry_datetime(self, expiry):
        datetime_format = self.get_expiry_datetime_format()
        return DateTimeField(format=datetime_format).to_representation(expiry)

    def get_post_response_data(self, request, token, instance, user):
        data = {"expiry": self.format_expiry_datetime(instance.expiry), "token": token}
        data["profile"] = UserSerializer(user).data
        return data

    def valid_email(self, email):
        if validate_email(address=email, check_dns=True):
            return {"email": email}

    def create_token(self, user):
        key = PassResetToken.objects.filter(user=user)
        if len(key):
            print(key)
            print("k") if key[0].delete() else print("s")
            token = PassResetToken.objects.create(user=user, token=tk())
            token.refresh_from_db()
        else:
            token = PassResetToken.objects.create(user=user, token=tk())
            token.refresh_from_db()

        return token

    def get_user(self, pk):
        try:
            user = User.objects.get(email=pk)
        except:
            return None
        return user

    def get_otp(self, user):
        totp = user.verification_device
        otp = totp.generate_challenge()

        key = OTPToken.objects.filter(Q(user=user))
        if len(key):
            print(key)
            print("k") if key[0].delete() else print("s")
            token = OTPToken.objects.create(user=user, token=tk())
            token.refresh_from_db()
        else:
            token = OTPToken.objects.create(user=user, token=tk())
            token.refresh_from_db()

        print(token.token)
        return [otp, token]

    def send_otp(self, user, otp):
        maildata = {
            "mail": EmailTemplate.objects.get(name="get-otp"),
            "context": {"otp": otp},
        }
        if user.email:
            Send_Mail.send(sender=user, data=maildata)
        return True

    def send_reset_link(self, user, token, request, e_or_p):
        reset_link = reverse(
            "accounts-pass_reset", kwargs={"pk": token.token}, request=request
        )
        maildata = {
            "mail": EmailTemplate.objects.get(name="get-reset-link"),
            "context": {"reset_link": reset_link},
        }

        print(reset_link)

        smsdata = {
            "message": f"Hi There Your Reset Link is {reset_link}",
        }
        if e_or_p.get("email"):
            Send_Mail.send(sender=user, data=maildata)
        return True


class OTPManagement:
    @action(methods=["get"], detail=True, url_name="get_otp", url_path="get-otp")
    def getotp(self, request, pk):
        user = self.get_user(pk)
        if user is not None:
            if not user.is_active:
                otp, token = self.get_otp(user)

                response = {
                    "Response": "Your Otp Has Been Sent To Your email",
                    "resend-otp": reverse(
                        "accounts-resend_otp", kwargs={"pk": pk}, request=request
                    ),
                    "verify-otp-url": reverse(
                        "accounts-otp_verification",
                        kwargs={"pk": token.token},
                        request=request,
                    ),
                }
                print(otp)
                return Response(response)

            return Response("Your Account Is Already Verified")
        return Response("User With This Key Not Exist")

    @action(
        methods=["post"],
        detail=True,
        url_name="otp_verification",
        url_path="otp-verification",
    )
    def verify_otp(self, request, pk):
        token = OTPToken.objects.filter(token=pk)
        if len(token):
            user = token[0].user
            if user.is_active:
                return Response("User Already Verified")
            totp = user.verification_device
            otp = request.data.get("otp")
            res = {
                "resend-otp": reverse(
                    "accounts-resend_otp", kwargs={"pk": pk}, request=request
                )
            }
            res["Response"] = "OTP is Required"
            if otp is not None:
                res["Response"] = "OTP is incorrect"
                if totp.verify_token(otp):
                    res = {"signin-url": reverse("accounts-signin", request=request)}
                    token.delete()
                    user.is_active = True
                    user.save()
                    user.refresh_from_db
                    return Response(res)
                return Response(res, status.HTTP_400_BAD_REQUEST)
            return Response(res)
        return Response("User With This Key Not Exist")

    @action(methods=["get"], detail=True, url_name="resend_otp", url_path="resend-otp")
    def resend_otp(self, request, pk):
        token = OTPToken.objects.filter(Q(token=pk))
        print(token)
        if len(token):
            user = token[0].user
            token.delete()
            if not user.is_active:
                otp, token = self.get_otp(user)
                response = {
                    "Response": "Your Otp Has Been Sent To Your email",
                    "Verify-OTP-Url": reverse(
                        "accounts-otp_verification",
                        kwargs={"pk": token.token},
                        request=request,
                    ),
                    "Resend-OTP": reverse(
                        "accounts-resend_otp",
                        kwargs={"pk": token.token},
                        request=request,
                    ),
                }
                self.send_otp(user, otp)
                print(otp)
                print(user)
                return Response(response)
            return Response("Your Account Is Already Verified")
        return Response("User With This Url Not Exist")


class PasswordManagement:
    @action(
        methods=["post"],
        detail=False,
        url_name="get_reset_link",
        url_path="get-reset-link",
    )
    def get_reset_link(self, request):
        email = self.valid_email(request.data.get("email"))
        if email is not None:
            try:
                user = User.objects.get(Q(email=request.data.get("email")))
            except:
                return Response(
                    "User With This email email Does Not Exist",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                "Email Or email Not Valid", status=status.HTTP_400_BAD_REQUEST
            )

        token = self.create_token(user=user)

        if self.send_reset_link(user, token, request, email):

            return Response("Reset Link Has Been Sent To Your Email")
        return Response(
            "Something Went Wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(
        methods=["post"], detail=True, url_name="pass_reset", url_path="password-reset"
    )
    def password_reset(self, request, pk):
        try:
            token = PassResetToken.objects.get(token=pk)
        except:
            return Response(
                "Your Token Is Expired Or Incorrect", status=status.HTTP_400_BAD_REQUEST
            )
        serializer = PasswordResetSerializer(
            data=request.data, context={"user": token.user}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {
                    "Response": "Your Password Has Been Reset",
                    "signin-url": reverse("accounts-signin", request=request),
                }
            )
        return Response(
            "Something Went Wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(
        methods=["post"],
        detail=False,
        url_name="change_pass",
        url_path="change-password",
        permission_classes=[IsAuthenticated],
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid:
            serializer.update(data=serializer.data)
            return Response("Password Change Successfull")
        return Response("Invalid", status=status.HTTP_400_BAD_REQUEST)


# Master Class Used In Urls
class AccountsManagement(
    Base, OTPManagement, PasswordManagement, viewsets.GenericViewSet
):
    http_method_names = ["post", "get", "delete"]
    serializer_class = SignUpSerializer

    def get_queryset(self):
        return None

    @action(methods=["post"], detail=False, url_name="signup", url_path="signup")
    def signup(self, request):
        data = request.data
        try:
            email = data.get("email").lower()
            data["email"] = email
        except:
            pass
        serializer = self.get_serializer(data=data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            user = User.object.filter(email=serializer.data.get("email").lower())
            res = {
                "User": serializer.data.get("email"),
                "Response": "Registration Succesfull Please verify Your Account",
            }
            print(len(user))
            if len(user):
                if not user[0].is_active:
                    otp, token = self.get_otp(user[0])
                    print(token)
                    print(otp)
                    res["Verify-OTP"] = (
                        reverse(
                            "accounts-otp_verification",
                            kwargs={"pk": token.token},
                            request=request,
                        ),
                    )[0]
                    res["Resend-OTP"] = reverse(
                        "accounts-resend_otp",
                        kwargs={"pk": token.token},
                        request=request,
                    )
                    res["Response"] = (
                        "User with This Email Or email Exist But Not Verified"
                    )
                    self.send_otp(user[0], otp)

                    print(otp)
                    return Response(res)

                return Response(
                    f"User with This Email Already Exist And Verified",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = serializer.create(data=serializer.data)
            otp, token = self.get_otp(user)
            print(token, otp)
            res["Verify-OTP"] = (
                reverse(
                    "accounts-otp_verification",
                    kwargs={"pk": token.token},
                    request=request,
                ),
            )
            res["Resend-OTP"] = reverse(
                "accounts-resend_otp", kwargs={"pk": token.token}, request=request
            )
            self.send_otp(user, otp)
            return Response(res)
        return Response({"status": 400})

    @action(methods=["post"], detail=False, url_name="signin", url_path="signin")
    def signin(self, request, format=None):

        token_limit_per_user = self.get_token_limit_per_user()
        serializer = SignInSerializer(data=request.data, context={"request": request})

        if serializer.is_valid(raise_exception=True):
            print("valid")
            data = serializer.data
            user = self.get_user(data["email"])

            if not user.is_active:
                otp, token = self.get_otp(user)
                print(token)
                print(otp)
                res = {
                    "Response": f"id: {user.id} is not verified yet",
                    "Verify-OTP": reverse(
                        "accounts-otp_verification",
                        kwargs={"pk": token.token},
                        request=request,
                    ),
                    "Resend-OTP": reverse(
                        "accounts-resend_otp",
                        kwargs={"pk": token.token},
                        request=request,
                    ),
                }
                self.send_otp(user, otp)
                return Response(res)

            if token_limit_per_user is not None:
                now = timezone.now()
                token = request.user.auth_token_set.filter(expiry__gt=now)
                if token.count() >= token_limit_per_user:
                    return Response(
                        {
                            "error": "Maximum amount of tokens allowed per user exceeded."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
            token_ttl = self.get_token_ttl()
            instance, token = AuthToken.objects.create(user, token_ttl)
            print(instance, token)
            data = self.get_post_response_data(
                request=request, token=token, instance=instance, user=user
            )
            print(data)
            return Response(data)

    @action(
        methods=["delete"],
        detail=False,
        url_name="delete_user",
        url_path="delete-user",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def delete_user(self, request):
        try:
            user = User.objects.get(user=request.user.user)
        except:
            return Response(
                "User With This Token Does Not Exist",
                status=status.HTTP_400_BAD_REQUEST,
            )
        password = request.data.get("password")
        if password is not None:
            if user.check_password(password):
                user.delete()
                return Response("Your Account Has Been Deleted")
            return Response("Password Is Incorrect", status=status.HTTP_400_BAD_REQUEST)
        return Response("Password Is Required", status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["post"],
        detail=False,
        url_name="fcmT",
        url_path="fcmT",
    )
    def get_notification_token(self, request):
        try:
            if request.data.get("fcm_old") is not None:
                noti = NotificationToken.objects.get(token=request.data.get("fcm_old"))
                noti.token = request.data.get("fcm_token")
        except Exception as e:
            NotificationToken.objects.create(token=request.data.get("fcm_old"))
            print(e)
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["get"],
        detail=False,
        url_name="get-notification",
        url_path="get-notification",
    )
    def get_notification(self, request):
        tkn = str(request.META.get("QUERY_STRING")).split("=")[1].replace("%3A", ":")
        print(tkn)
        try:
            token = NotificationToken.objects.filter(token=tkn)
            query = Notification.objects.filter(Q(token=token[0]))
            serializer = NotificationSerializer(query, many=True)
        except Exception as e:
            print(e)
            return Response("some error", status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["get"],
        detail=False,
        url_name="logout",
        url_path="logout",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def logout(self, request):
        for token in NotificationToken.objects.filter(user=request.user):
            token.user = None
            token.save()
        AuthToken.objects.filter(user=request.user.id).delete()
        return Response(status=status.HTTP_200_OK)
