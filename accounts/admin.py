from django.contrib import admin

from django.contrib.sessions.models import Session

from accounts.models.UserModel import User, PassResetToken, Salt
from accounts.models.OTPModel import VerificationDevice, OTPToken



class VerificationDeviceInline(admin.StackedInline):
    model = VerificationDevice


# class PortfolioPostInline(admin.StackedInline):
#     model = PortfolioPost

# class PostImageInline(admin.StackedInline):
#     model = PostImage

# class ClientPostImageInline(admin.StackedInline):
#     model = ClientPost

# class EducationInline(admin.StackedInline):
#     model = Education

# class ExperienceInline(admin.TabularInline):
#     model = Experience

# @admin.register(ClientPost)
# class Admin(admin.ModelAdmin):
#     inlines = [ClientPostImageInline]

# @admin.register(PortfolioPost)
# class Admin(admin.ModelAdmin):
#     inlines = [PostImageInline]

# @admin.register(Portfolio)
# class Admin(admin.ModelAdmin):
#     inlines = [PortfolioPostInline, EducationInline, ExperienceInline]

@admin.register(User)
class Admin(admin.ModelAdmin):
    # inlines = [UserProfileInline, VerificationDeviceInline]
    list_display = ('__str__',)


@admin.register(PassResetToken)
class PassRestTokenAdmin(admin.ModelAdmin):
    list_display = ('user',)

# @admin.register(Locations)
# class PlaceAdmin(OSMGeoAdmin):
#     list_display=('city',)

admin.site.register(Session)
admin.site.register(OTPToken)
# admin.site.register(Skill)

@admin.register(Salt)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('salt', 'nonce')