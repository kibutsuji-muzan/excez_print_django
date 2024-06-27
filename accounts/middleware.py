from django.contrib.sessions.models import Session
from accounts.models.UserModel import PassResetToken
from accounts.models.OTPModel import OtpToken
from django.utils import timezone
from django.conf import settings

class OneSessionPerUserMiddleware:

    # Called only once when the web server starts
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            stored_session_key = request.user.logged_in_user.session_key
            if stored_session_key and stored_session_key != request.session.session_key:
                 Session.objects.get(session_key=stored_session_key).delete()

            request.user.logged_in_user.session_key = request.session.session_key
            request.user.logged_in_user.save()

        response = self.get_response(request)
        return response

class DeleteExpiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now=timezone.now()
        otp_token = OtpToken.objects.all()
        pass_token = PassResetToken.objects.all()

        if len(otp_token):
            for token in otp_token:
                if (token.expiry <= now):
                    token.delete()
        if len(pass_token):
            for token in pass_token:
                if (token.expiry <= now):
                    token.delete()
        response = self.get_response(request)
        return response
    
class ActivateTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timezone.activate(settings.TIME_ZONE)
        response = self.get_response(request)
        return response
    