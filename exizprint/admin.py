from django.contrib import admin
from exizprint.models.services import Services,FormFieldName,FormFieldType
# Register your models here.


admin.site.register(FormFieldType)


class FormFieldInline(admin.TabularInline):
    model = FormFieldName

@admin.register(Services)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [FormFieldInline]