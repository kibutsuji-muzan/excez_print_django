from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django_otp.util import hex_validator, random_hex
from django.utils import timezone

from accounts.usermanager import UserManager

from upload_validator import FileTypeValidator
from datetime import timedelta
from hashlib import pbkdf2_hmac, sha256
import random
import uuid

# drop schema public cascade;create schema public;grant all on schema public to admin;
#CREATE EXTENSION postgis;

ranint = lambda a,b:random.randint(a,b)

def get_salt():
    salt = Salt.objects.all()
    if len(salt):
        salt.delete()
    return Salt.objects.create()

def default_key(a):
    return random_hex(a)

def dk(e_or_p):
    return sha256(bytes(e_or_p,'utf-8')).hexdigest()

def token():
    salt = get_salt()
    return pbkdf2_hmac('sha256', bytes(str(default_key(20)),'utf-8'), bytes(str(salt.salt),'utf-8')*ranint(2,9), int(salt.nonce)).hex()

def expiryTime(m):
    now = timezone.now()
    return now+timedelta(minutes=5 if m else 15)


class Salt(models.Model):

    id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
    salt = models.CharField(_('Salt'), default=default_key(ranint(25,30)), null=False, blank=False)
    nonce = models.CharField(_('Nonce'), default=ranint(9999,99999), null=False, blank=False)

    def __str__(self):
        return self.salt

class User(AbstractUser):

    username = None
    first_name = None
    last_name = None
    id= None

    user = models.CharField(_("Username"), max_length=70, unique=True, validators=[hex_validator])

    created_at = models.DateTimeField(auto_now=True,editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    object = UserManager()

    USERNAME_FIELD = 'user'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

class PassResetToken(models.Model):

    id = models.UUIDField(_('UUID'), default=uuid.uuid4, null=False , primary_key=True, editable=False)
    user = models.OneToOneField(User, verbose_name=_("User"), on_delete=models.CASCADE, related_name='reset_token')
    token = models.CharField(_("Token-Key"), max_length=70, unique=True)
    expiry = models.DateTimeField(_("Expiry"), auto_now=False, auto_now_add=False, default=expiryTime(False))
    created_at = models.DateTimeField(_("Ceated At"), auto_now_add=True)

    def __str__(self):
        return self.token

class UserProfile(models.Model):
    GENDER = [('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('OTHER', 'OTHER')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, editable=True, unique=True, verbose_name=_("User"), related_name='user_profile')

    first_name = models.CharField(_('First Name'), max_length=20, blank=False, null=True)
    last_name = models.CharField(_('Last Name'), max_length=20, blank=False, null=True)

    email = models.EmailField(_('Email'), max_length=200, blank=True, null=True)

    gender = models.CharField(_('Gender'),choices=GENDER, max_length=6, blank=False, null=True)
    birthday = models.DateField(_('Birth Date'), blank=False, null=True)
    
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.email) if str(self.email) else str(self.phone)

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
