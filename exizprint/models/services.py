from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models.UserModel import User
import uuid

from upload_validator import FileTypeValidator
from gdstorage.storage import GoogleDriveStorage, GoogleDrivePermissionType, GoogleDrivePermissionRole, GoogleDriveFilePermission

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

class Services(models.Model):
     id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
     parent = models.ForeignKey('Services',on_delete=models.CASCADE,null=True,blank=True)
     name = models.CharField(_('Service Name'), max_length=20, blank=False, null=True)
     desc = models.CharField(_('Description'), max_length=150, blank=True, null=True)
     image = models.ImageField(_("Image"), upload_to="ServiceImage/", default="ProfileImages/download.jpeg", validators=[FileTypeValidator(allowed_types=[ 'image/*'])])
     rate = models.IntegerField(_("Price"), null=True,blank=True)
     def __str__(self):
        return str(self.name)

     class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

class FormFieldName(models.Model):
    types = [('txt', 'Text'), ('ch', 'Choices'), ('int', 'Number'), ('file', 'File')]
    id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
    service = models.ForeignKey(Services, on_delete=models.RESTRICT,null=True,related_name='field')
    field_name = models.CharField(_('Field'),max_length=20,null=True)
    value = models.CharField(_('values if needed'),null=True,blank=True)
    field_type = models.CharField(_("FormFieldType"),choices=types)

class Orders(models.Model):
    STATUS = [('unpaid', 'unpaid'),('paid', 'paid'),('pending', 'pending'), ('in_progress', 'in_progress'), ('done', 'done'), ('cancelled', 'cancelled')]
    
    id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
    service = models.ForeignKey(Services,on_delete=models.RESTRICT,null=False, related_name='order_of')
    eta = models.DateField(_("ETA"),null=True,blank=True)
    bill = models.IntegerField(_("Price"), null=True,blank=True)
    payment_status = models.BooleanField(_("Payment Status"), default=False)
    status = models.CharField(_('Status'),choices=STATUS, blank=True, null=True, default='unpaid')

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, related_name='orders')

class KeyValue(models.Model):
    id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
    key = models.CharField(_('Key'),null=False,blank=False)
    value = models.CharField(_('Value'),null=False,blank=False)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE,null=False,blank=False)

class NotificationToken(models.Model):
    token = models.CharField(_('FCM Token'), blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='fcmtoken')

    def __str__(self):
        return self.token
    
class Notification(models.Model):
    message = models.CharField(max_length=100,null=True, blank=True)
    title = models.CharField(max_length=100,null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to="ServiceImage/",validators=[FileTypeValidator(allowed_types=[ 'image/*'])], null=True, blank=True)
    token  = models.ManyToManyField(NotificationToken, null=False, blank=False, related_name='fcm_token')
    created_at = models.DateTimeField(auto_now=True,editable=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name='noti_of')

    def __str__(self):
        return str(self.title)
    
class Banner(models.Model):
    image = models.ImageField(_("Image"), upload_to="ServiceImage/",validators=[FileTypeValidator(allowed_types=[ 'image/*'])], null=False, blank=False)
    def __str__(self):
        return str(self.image)

class FileField(models.Model):
    id = models.AutoField(primary_key=True)
    field_name = models.CharField(_("Field Name"),max_length=200)
    file= models.FileField(_("File"),upload_to='', storage=gd_storage, validators=[validator])
    order = models.ForeignKey(Orders,on_delete=models.CASCADE,null=False, blank=False)

class PaymentModel(models.Model):
    razorpay_order_id =  models.CharField(max_length=100,null=False, blank=False)
    razorpay_payment_id =  models.CharField(max_length=100,null=False, blank=False)
    razorpay_signature =  models.CharField(max_length=100,null=False, blank=False)
    ordr = models.ForeignKey(Orders,on_delete=models.DO_NOTHING,null=False, blank=False)