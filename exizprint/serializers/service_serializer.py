import os
from rest_framework import serializers
from core import settings
from exizprint.models.services import (
    Services,
    FormFieldName,
    Orders,
    KeyValue,
    Notification,
    Banner,
    FileField,
    PaymentModel,
    TempFileField,
)
from core.task import SendMail, upload_to_google
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File


class FormFieldNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = FormFieldName
        fields = ["field_name", "value", "field_type"]


class ServiceSerializer(serializers.ModelSerializer):
    field = FormFieldNameSerializer(many=True)

    class Meta:
        model = Services
        fields = ["name", "id", "desc", "field", "parent", "image", "rate"]


class SerializerOrder(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Orders
        fields = ["id", "service", "status", "eta"]


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyValue
        depth = 1
        fields = ["key", "value"]


class OrderSerializer(serializers.ModelSerializer):

    # order_detail = OrderDetailSerializer(read_only=True, many=True)

    class Meta:
        model = Orders
        fields = ["service"]

    def validate(self, data):

        print("\n")
        print("\n")
        print(self.context.get("fields").keys())
        print("\n")
        print("\n")
        ser_fields = FormFieldName.objects.filter(service=self.context.get("service"))
        s_fields = self.context.get("fields").copy()
        for field in ser_fields:
            if field.field_type == "file":
                if field.field_name not in self.context.get("request").FILES:
                    raise serializers.ValidationError(
                        f"{field.field_name} field is required"
                    )
                self.context.get("files")[field.field_name] = self.context.get(
                    "request"
                ).FILES[field.field_name]
                self.context.get("fields").pop(field.field_name)
            else:
                if field.field_name not in self.context.get("fields").keys():
                    raise serializers.ValidationError(
                        f"{field.field_name} field is required"
                    )
        return data

    def create(self, data):
        print(f"data:{data}")
        ordr = self.Meta.model.objects.create(
            user=self.context.get("request").user,
            service=self.context.get("service"),
            bill=self.context.get("service").rate,
        )
        self.context.get("id")["id"] = ordr.id

        for key, value in self.context.get("fields").items():
            print(f"{key}, {value}")
            KeyValue.objects.create(order=ordr, key=key, value=value)
        for key, value in self.context.get("files").items():
            tempFile = TempFileField.objects.create(temp_file=value)
            upload_to_google.delay(key=key, ordr_id=ordr.id, temp_id=tempFile.id)
        maildata = {
            "mail": "order-placed",
            "context": {"order_id": ordr.id, "service":self.context.get("service").name, "bill":self.context.get("service").rate},
            "email": self.context.get("request").user.email,
            "priority": "now",
        }
        SendMail.delay(data=maildata)
        return data


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["message", "title", "image", "created_at"]


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ["image"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModel
        fields = ["razorpay_order_id", "razorpay_payment_id", "razorpay_signature"]
