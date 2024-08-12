import json
from django.dispatch import receiver, Signal
from django.db.models.signals import post_save
from accounts.models.OTPModel import VerificationDevice
from accounts.models.UserModel import User
from core import settings

from post_office import mail, models
from exizprint.models.services import Notification, Orders, NotificationToken
from firebase_admin import messaging

from core.task import SendMail


# def send_email_task(subject, message, from_email, recipient_list):
#     send_mail(subject, message, from_email, recipient_list)



# @receiver(Send_Mail)
# def SendMail(sender, data, **kwargs):
#     maildata = data.get("mail")
#     context = data.get("context")
#     mail.send(
#         [
#             sender.email,
#         ],
#         settings.EMAIL_HOST_USER,
#         subject=maildata.subject,
#         message=maildata.content,
#         html_message=maildata.html_content,
#         context=context,
#         priority="now",
#     )


@receiver(post_save, sender=User)
def createOtp(sender, instance, created, **kwargs):
    if created:
        VerificationDevice.objects.get_or_create(user=instance)


@receiver(post_save, sender=Orders)
def on_change(sender, instance, created, **kwargs):
    tokens = NotificationToken.objects.filter(user=instance.user)
    notification = Notification.objects.create(
        title="Order Status Update",
        message=f"Your Status For Order {instance.service.name} is Updated to {instance.status}",
        user = instance.user
    )
    maildata = {
        "mail": "service-update",
        "email": instance.user.email,
        "priority": "now",
    }
    SendMail.delay(maildata)
    print("order update")
    for tkn in tokens:
        notification.token.add(tkn)
        notification.save()


@receiver(post_save, sender=Notification)
def send_push_notification(sender, instance, created, **kwargs):
    if instance.image == None:
        noti = (
            messaging.Notification(
                title=instance.title,
                body=instance.message,
            ),
        )
    else:
        noti = (
            messaging.Notification(
                title=instance.title, body=instance.message, image=str(f'https://{settings.ALLOWED_HOSTS[0]}/media/{instance.image}')
            ),
        )
    print(f'https://{settings.ALLOWED_HOSTS[0]}/media/{instance.image}')
    for tkn in instance.token.all():
        message = messaging.Message(
            token=str(tkn),
            notification=noti[0],
            data=None,
        )
        try:
            response = messaging.send(message)
            print("notification send")
            return response
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
