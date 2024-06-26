from django.dispatch import receiver, Signal
from django.db.models.signals import post_save  # pre_save,

# from django.contrib.auth import user_logged_in, user_logged_out

from accounts.models.OTPModel import VerificationDevice
from accounts.models.UserModel import User
from core import settings

from post_office import mail
from sms import send_sms

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from exizprint.models.services import Notification, Orders
from firebase_admin import messaging


Send_Mail = Signal()
Send_Sms = Signal()
Create_Profile = Signal()
Send_Notification = Signal()


@receiver(Send_Mail)
def SendMail(sender, data, **kwargs):
    maildata = data.get("mail")
    context = data.get("context")
    mail.send(
        [
            sender.email,
        ],
        settings.EMAIL_HOST_USER,
        subject=maildata.subject,
        message=maildata.content,
        html_message=maildata.html_content,
        context=context,
        priority="now",
    )


# @receiver(Send_Sms)
# def SendSms(sender, data, **kwargs):
#     send_sms(data.get('message'), settings.DEFAULT_FROM_SMS, [str(sender.phone),], fail_silently=False, priority='now')

# @receiver(Create_Profile)
# def createProfile(sender, data, email_phone, **kwargs):
#     print(data)
#     print(email_phone)

#     if email_phone.get('email'):
#         user = UserProfile.objects.create(email = email_phone.get('email'),user = sender, gender = data.get('gender'), birthday = data.get('birthday'), first_name = data.get('first_name'), last_name = data.get('last_name'))
#     else:
#         user = UserProfile.objects.create(phone = email_phone.get('phone'),user = sender, gender = data.get('gender'), birthday = data.get('birthday'), first_name = data.get('first_name'), last_name = data.get('last_name'))

#     print(user)
#     for id in data.get('type'):
#         user.type.add(id)


@receiver(post_save, sender=User)
def createOtp(sender, instance, created, **kwargs):
    if created:
        VerificationDevice.objects.get_or_create(user=instance)


# @receiver(post_save, sender=UserProfile)
# def createProfileImage(sender, instance, created, **kwargs):
#     if created:
#         ProfileImage.objects.create(profile=instance)

# @receiver(user_logged_in)
# def on_user_logged_in(sender, request, **kwargs):
#     LoggedInUser.objects.get_or_create(user=kwargs.get('user'))


# @receiver(user_logged_out)
# def on_user_logged_out(sender, **kwargs):
#     LoggedInUser.objects.filter(user=kwargs.get('user')).delete()


# @receiver(post_save, sender=Notification)
# def notification_created(sender, instance, created, **kwargs):
#     if created:
#         channel_layer = get_channel_layer()
#         print(channel_layer)
#         print(instance.message)
#         async_to_sync(channel_layer.group_send)(
#             "public_room", {"type": "send_notification", "message": instance.message}
#         )


@receiver(post_save, sender=Orders)
def on_change(sender, instance, created, **kwargs):
    print(instance.user.fcmtoken)
    Notification.objects.create(
        title="Order Status Update",
        message=f"Your Status For Order {instance.service.name} is Updated to {instance.status}",
        token=instance.user.fcmtoken,
    )


@receiver(post_save, sender=Notification)
def send_push_notification(sender, instance, created, **kwargs):
    if(instance.image == None):
        noti=messaging.Notification(
                title=instance.title,
                body=instance.message,
            ),
    else:
        noti=messaging.Notification(
                title=instance.title,
                body=instance.message,
                image=str(instance.image)
            ),
    print(noti[0].title)
    message = messaging.Message(
        token=str(instance.token),
        notification=noti[0],
        data=None,
    )
    try:
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f"Error sending message: {e}")
        return None
