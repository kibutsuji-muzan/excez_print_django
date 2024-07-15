import os
from celery import shared_task
from django.core.files.base import ContentFile

from post_office import mail, models
from accounts.models.UserModel import User
from core import settings
from exizprint.models.services import FileField, TempFileField, Orders


@shared_task(bind=True)
def SendMail(self, data):
    print("data")
    try:
        maildata = models.EmailTemplate.objects.get(name=data["mail"])
        context = data["context"]
        mail.send(
        [
            data["email"],
        ],
        settings.EMAIL_HOST_USER,
        subject=maildata.subject,
        message=maildata.content,
        html_message=maildata.html_content,
        context=context,
        priority=data["priority"],
        )
    except:
        return data
    return "Done"


@shared_task(bind=True)
def upload_to_google(self, key, ordr_id, temp_id):
    try:
        tempFile = TempFileField.objects.get(id=temp_id)
        order = Orders.objects.get(id=ordr_id)
        with open(str(tempFile.temp_file.file), 'rb') as f:
            FileField.objects.create(
                field_name=key,
                order=order,
                file=ContentFile(f.read(), f'{tempFile.temp_file.name}'.split('/')[1]),
            )
            f.close()
        tempFile.deleteTemp()
        tempFile.delete()
    except Exception as e:
        mail.send(
            [
                "ansari.kaifi7348@gmail.com",
            ],
            settings.EMAIL_HOST_USER,
            subject="Some error have occued in uploading file",
            message=str(e),
            priority="now",
        )
        return f"Error Have Occured {e}"
    return f"completed "
