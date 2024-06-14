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
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_authenticated:
            stored_session_key = request.user.logged_in_user.session_key

            # client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
            # user_agent = request.META['HTTP_USER_AGENT']

            # if there is a stored_session_key  in our database and it is
            # different from the current session, delete the stored_session_key
            # session_key with from the Session table
            if stored_session_key and stored_session_key != request.session.session_key:
                 Session.objects.get(session_key=stored_session_key).delete()

            # request.user.logged_in_user.user_agent = user_agent
            # request.user.logged_in_user.client_ip = client_ip
            request.user.logged_in_user.session_key = request.session.session_key
            request.user.logged_in_user.save()

        response = self.get_response(request)

        # This is where you add any extra code to be executed for each request/response after
        # the view is called.
        # For this tutorial, we're not adding any code so we just return the response

        return response

class DeleteExpiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now=timezone.now()
        # now=datetime(hour=int(now.strftime('%H')), minute=int(now.strftime('%M')), second=int(now.strftime('%S')))
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
    