from django.contrib import admin

from django.contrib.sessions.models import Session

from accounts.models.UserModel import User, PassResetToken, Salt
from accounts.models.OTPModel import VerificationDevice, OTPToken



class VerificationDeviceInline(admin.StackedInline):
    model = VerificationDevice

@admin.register(User)
class Admin(admin.ModelAdmin):
    list_display = ('__str__',)


@admin.register(PassResetToken)
class PassRestTokenAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(Session)
admin.site.register(OTPToken)

@admin.register(Salt)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('salt', 'nonce')