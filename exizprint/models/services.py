from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class Services(models.Model):
     id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
     parent = models.ForeignKey('Services',on_delete=models.CASCADE,null=True,blank=True)
     name = models.CharField(_('Service Name'), max_length=20, blank=False, null=True)
     desc = models.CharField(_('Description'), max_length=150, blank=True, null=True)

     def __str__(self):
        return str(self.name)

     class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

class FormFieldType(models.Model):
    name = models.CharField(_('Field Type'),max_length=20)
    def __str__(self):
        return self.name

class FormFieldName(models.Model):
    Service = models.ForeignKey(Services, on_delete=models.RESTRICT,null=True)
    field_name = models.CharField(_('Field'),max_length=20,null=True)
    value = models.CharField(_('values if needed'),null=True,blank=True)
    field_type = models.ForeignKey(FormFieldType,on_delete=models.RESTRICT)