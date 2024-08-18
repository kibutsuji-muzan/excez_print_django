from django.contrib import admin
from exizprint.models.services import Services,FormFieldName, Orders, KeyValue, NotificationToken, Notification,Banner, FileField, PaymentModel, ServiceRate, CheckOut

admin.site.register(NotificationToken)
admin.site.register(Banner)
admin.site.register(PaymentModel)
admin.site.register(CheckOut)


class FormFieldInline(admin.TabularInline):
    model = FormFieldName
    extra = 0

class FileFieldInline(admin.TabularInline):
    model = FileField
    extra = 0

class PriceServiceInline(admin.TabularInline):
    model = ServiceRate
    extra = 0

class KeyValueInline(admin.TabularInline):
    model = KeyValue
    extra = 0

@admin.register(Services)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [FormFieldInline, PriceServiceInline]

@admin.register(Orders)
class OrderAdmin(admin.ModelAdmin):
    inlines = [KeyValueInline, FileFieldInline]

@admin.action(description="Execute Signal")
def execute_signal(modeladmin, request, queryset):
    print('data')
#     for obj in queryset:
#         my_signal.send(sender=MyModel, instance=obj)

class MyModelAdmin(admin.ModelAdmin):
    actions = [execute_signal]

admin.site.register(Notification)