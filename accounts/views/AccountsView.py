from accounts.serializers.AccountSerializer import (
    SignUpSerializer,
    SignInSerializer,
    PasswordResetSerializer,
    ChangePasswordSerializer,
)
from accounts.serializers.ProfileSerializer import ProfileSerializer

from accounts.models.UserModel import User, PassResetToken, dk, token as tk
from accounts.models.OTPModel import OTPToken
from accounts.signals import Send_Mail, Send_Sms
from core import settings
from accounts.permissions import IsSameUser

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

#------------------------------------------------------------#
#-------- Implement Logout User Later In Next Commit --------#
#------------------------------------------------------------#

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
        data["profile"] = ProfileSerializer(user.user_profile).data
        return data
        
    def valid_email_phone(self, email_or_phone):
        if validate_email(address=email_or_phone, check_dns=True):
            return {'email': email_or_phone, 'phone': False}
        try:
            if validate_phone(email_or_phone):
                return {'phone': email_or_phone, 'email': False}
        except:
            raise None

    def create_token(self, user):
        key = PassResetToken.objects.filter(user=user)
        if len(key):
            print(key)
            print('k') if key[0].delete() else print('s')
            token = PassResetToken.objects.create(user=user, token=tk())
            token.refresh_from_db()
        else:
            token = PassResetToken.objects.create(user=user, token=tk())
            token.refresh_from_db()

        return token

    def get_user(self, pk):
        try:
            user = User.objects.get(user=pk)
        except:
            return None
        return user

    def get_otp(self, user):
        totp = user.verification_device
        otp = totp.generate_challenge()
        
        key = OTPToken.objects.filter(Q(user=user))
        if len(key):
            print(key)
            print('k') if key[0].delete() else print('s')
            token = OTPToken.objects.create(user=user, token=tk())
            token.refresh_from_db()
        else:
            token = OTPToken.objects.create(user=user, token=tk())
            token.refresh_from_db()

        print(token.token)
        return [otp, token]

    def send_otp(self, user, otp):
        smsdata = {
            "message": f"Hi There Your Otp is {otp}",
        }
        maildata = {
            "mail": EmailTemplate.objects.get(name="get-otp"),
            "context": {"otp": otp},
        }
        if user.user_profile.email:
            Send_Mail.send(sender=user.user_profile, data=maildata)
        if user.user_profile.phone:
            Send_Sms.send(sender=user.user_profile, data=smsdata)
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
        if e_or_p.get('email'):
            Send_Mail.send(sender=user.user_profile, data=maildata)
        if e_or_p.get('phone'):
            Send_Sms.send(sender=user.user_profile, data=smsdata)
        return True

class OTPManagement:
    @action(methods=["get"], detail=True, url_name="get_otp", url_path="get-otp")
    def getotp(self, request, pk):
        user = self.get_user(pk)
        if user is not None:
            if not user.is_active:
                otp, token = self.get_otp(user)

                response = {
                    "response": "Your Otp Has Been Sent To Your Phone",
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
            res["response"] = "OTP is Required"
            if otp is not None:
                res["response"] = "OTP is incorrect"
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
                    "Response": "Your Otp Has Been Sent To Your Phone",
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
        email_or_phone = self.valid_email_phone(request.data.get("email_or_phone"))
        if email_or_phone is not None:
            try:
                user = User.objects.get(Q(user=dk(request.data.get("email_or_phone"))))
            except:
                return Response(
                    "User With This email phone Does Not Exist",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                "Email Or Phone Not Valid", status=status.HTTP_400_BAD_REQUEST
            )

        token = self.create_token(user=user)

        if self.send_reset_link(user, token, request, email_or_phone):
  
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
                    "response": "Your Password Has Been Reset",
                    "signin-url": reverse("accounts-signin", request=request),
                }
            )
        return Response(
            "Something Went Wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @action(
        methods=["post"],
        detail=True,
        url_name="change_pass",
        url_path="change-password",
        permission_classes=[IsAuthenticated, IsSameUser],
    )
    def change_password(self, request, pk):
        serializer = ChangePasswordSerializer(data=request.data, context={"user": request.user})
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
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            u=dk(e_or_p=serializer.data.get("email_or_phone"))
            print(u)
            user = User.object.filter(user=u)
            res = {
                "User": serializer.data.get("email_or_phone"),
                "Response": "Registration Succesfull Please verify Your Account"
            }
            print(len(user))
            if len(user):
                if user[0].is_active:
                    if user[0].user_profile.email:
                        e_or_p = "Email"
                    if user[0].user_profile.phone:
                        e_or_p = "Phone"
                else:
                    otp, token = self.get_otp(user[0])
                    res['Verify-OTP'] = reverse("accounts-otp_verification", kwargs={"pk": token.token}, request=request),
                    res['Resend-OTP'] = reverse("accounts-resend_otp", kwargs={"pk": token.token}, request=request)
                    res["Response"] = "User with This Email Or Phone Exist But Not Verified"
                    self.send_otp(user[0], otp)

                    print(otp)
                    return Response(res)

                return Response(f"User with This '{e_or_p}' Already Exist And Verified")

            user = serializer.create(data=serializer.data)
            otp, token = self.get_otp(user)
            print(token,otp)
            res['Verify-OTP'] = reverse("accounts-otp_verification", kwargs={"pk": token.token}, request=request),
            res['Resend-OTP'] = reverse("accounts-resend_otp", kwargs={"pk": token.token}, request=request)
            self.send_otp(user, otp)
            return Response(res)
        return Response({"status": 400})

    @action(methods=["post"], detail=False, url_name="signin", url_path="signin")
    def signin(self, request, format=None):
        
        token_limit_per_user = self.get_token_limit_per_user()
        serializer = SignInSerializer(
            data=request.data, context={"TTL": token_limit_per_user, "request": request}
        )

        if serializer.is_valid(raise_exception=True):
            data = serializer.data
            id = dk(data["email_or_phone"])

            user = self.get_user(id)

            if not user.is_active:
                otp, token = self.get_otp(user)
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
        detail=True,
        url_name="delete_user",
        url_path="delete-user",
        permission_classes=[IsAuthenticated, IsSameUser],
    )
    def delete_user(self, request, pk):
        try:
            user = User.objects.get(user=request.user.user)
        except:
            return Response(
                "User With This Token Does Not Exist",
                status=status.HTTP_400_BAD_REQUEST,
            )
        password=request.data.get("password")
        if password is not None:
            if user.check_password(password):
                user.delete()
                return Response("Your Account Has Been Deleted")
            return Response("Password Is Incorrect", status=status.HTTP_400_BAD_REQUEST)
        return Response("Password Is Required", status=status.HTTP_400_BAD_REQUEST)        