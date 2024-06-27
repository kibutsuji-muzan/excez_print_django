from django.contrib import admin
from exizprint.models.services import Services,FormFieldName,FormFieldType, Orders, KeyValue, NotificationToken, Notification,Banner
# Register your models here.


admin.site.register(FormFieldType)
admin.site.register(NotificationToken)
admin.site.register(Notification)
admin.site.register(Banner)


class FormFieldInline(admin.TabularInline):
    model = FormFieldName

class KeyValueInline(admin.TabularInline):
    model = KeyValue

@admin.register(Services)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [FormFieldInline]

@admin.register(Orders)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [KeyValueInline]