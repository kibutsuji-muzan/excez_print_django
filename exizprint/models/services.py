import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models.UserModel import User
import uuid

from upload_validator import FileTypeValidator
from gdstorage.storage import GoogleDriveStorage, GoogleDrivePermissionType, GoogleDrivePermissionRole, GoogleDriveFilePermission

from core import settings

from phonenumber_field.modelfields import PhoneNumberField

validator = FileTypeValidator(
    allowed_types=['application/pdf', 'image/jpg', 'image/jpeg', 'image/png'],
    allowed_extensions=['.png', '.jpg', '.jpeg','.pdf']
)

permission =  GoogleDriveFilePermission(
   GoogleDrivePermissionRole.WRITER,
   GoogleDrivePermissionType.USER,
   "exizprint@vaulted-night-428015-c9.iam.gserviceaccount.com"
)
# Define Google Drive Storage
gd_storage = GoogleDriveStorage(permissions=(permission,))

class CheckOut(models.Model):
    id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
    address = models.CharField(_("address"),max_length=100,null=False, blank=False)
    first_name = models.CharField(_("First Name"),max_length=100,null=False, blank=False)
    last_name = models.CharField(_("Last Name"),max_length=100,null=False, blank=False)
    pin_code = models.IntegerField(_("Pin Code"),null=False, blank=False)
    house_number = models.CharField(_("House Number"),max_length=100,null=False, blank=False)
    phone_number = PhoneNumberField(_("Phone Number"),region="IN", null = False)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='checkout')

class Services(models.Model):
     id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
     name = models.CharField(_('Service Name'), max_length=20, blank=False, null=True)
     parent = models.ForeignKey('Services',on_delete=models.CASCADE,null=True,blank=True)
     desc = models.TextField(_('Description'), blank=True, null=True)
     image = models.ImageField(_("Image"), upload_to="ServiceImage/", validators=[FileTypeValidator(allowed_types=[ 'image/*'])])
     def __str__(self):
        return str(self.name)

     class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

class ServiceImages(models.Model):
     id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
     title = models.CharField(_('Service Title'), max_length=20, blank=True, null=True)
     image = models.ImageField(_("Image"), upload_to="ServiceImage/", validators=[FileTypeValidator(allowed_types=[ 'image/*'])])
     service = models.ForeignKey(Services, on_delete=models.SET_NULL,null=True,related_name='images')

class FormFieldName(models.Model):
    types = [('txt', 'Text'), ('ch', 'Choices'), ('int', 'Number'), ('file', 'File')]
    id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
    service = models.ForeignKey(Services, on_delete=models.SET_NULL,null=True,related_name='field')
    field_name = models.CharField(_('Field'),max_length=20,null=True)
    value = models.CharField(_('values if needed'),null=True,blank=True)
    field_type = models.CharField(_("FormFieldType"),choices=types)

class ServiceRate(models.Model):
    service = models.ForeignKey(Services, on_delete=models.CASCADE,related_name='price')
    above = models.FloatField(_('Above Quantity'),null=True,blank=True)
    price = models.FloatField(_('Rate Per Pcs.'),null=True,blank=True)

class Orders(models.Model):
    STATUS = [('unpaid', 'unpaid'),('paid', 'paid'),('pending', 'pending'), ('in_progress', 'in_progress'), ('done', 'done'), ('cancelled', 'cancelled')]
    
    id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
    service = models.ForeignKey(Services,on_delete=models.SET_NULL,null=True, related_name='order_of')
    eta = models.DateField(_("ETA"),null=True,blank=True)
    bill = models.FloatField(_("Price"), null=False,blank=False)
    quantity = models.IntegerField(_("Quantity"), null=False,blank=False)
    payment_status = models.BooleanField(_("Payment Status"), default=False)
    status = models.CharField(_('Status'),choices=STATUS, blank=True, null=True, default='unpaid')
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, related_name='orders')
    checkout = models.ForeignKey(CheckOut,on_delete=models.SET_NULL,null=True, blank=True)

class KeyValue(models.Model):
    id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
    key = models.CharField(_('Key'),null=False,blank=False)
    value = models.CharField(_('Value'),null=False,blank=False)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE,null=False,blank=False)

class NotificationToken(models.Model):
    token = models.CharField(_('FCM Token'), blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fcmtoken')

    def __str__(self):
        return self.token
    
class Notification(models.Model):
    message = models.CharField(max_length=100,null=True, blank=True)
    title = models.CharField(max_length=100,null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to="ServiceImage/",validators=[FileTypeValidator(allowed_types=[ 'image/*'])], null=True, blank=True)
    token  = models.ManyToManyField(NotificationToken, blank=False, related_name='fcm_token')
    created_at = models.DateTimeField(auto_now=True,editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='noti_of')

    def __str__(self):
        return str(self.title)
    
class Banner(models.Model):
    image = models.ImageField(_("Image"), upload_to="ServiceImage/",validators=[FileTypeValidator(allowed_types=[ 'image/*'])], null=False, blank=False)
    def __str__(self):
        return str(self.image)

class FileField(models.Model):
    id = models.AutoField(primary_key=True)
    field_name = models.CharField(_("Field Name"),max_length=200)
    file= models.FileField(_("File"),upload_to='', storage=gd_storage,null=True,blank=True,validators=[validator])
    order = models.ForeignKey(Orders,on_delete=models.CASCADE,null=False, blank=False)

class TempFileField(models.Model):
    id = models.AutoField(primary_key=True)
    temp_file = models.FileField(_("Temp File"),upload_to='Temp/',null=True,blank=True,validators=[validator])

    def deleteTemp(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.temp_file.name))

class PaymentModel(models.Model):
    razorpay_order_id =  models.CharField(max_length=100,null=False, blank=False)
    razorpay_payment_id =  models.CharField(max_length=100,null=False, blank=False)
    razorpay_signature =  models.CharField(max_length=100,null=False, blank=False)
    ordr = models.ForeignKey(Orders,on_delete=models.SET_NULL,null=True, blank=False)

