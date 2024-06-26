from rest_framework import serializers
from exizprint.models.services import (
    Services,
    FormFieldName,
    FormFieldType,
    Orders,
    KeyValue,
    Notification,
)


class FieldTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FormFieldType
        fields = ["name"]


class FormFieldNameSerializer(serializers.ModelSerializer):
    fieldtype = serializers.SerializerMethodField()

    class Meta:
        model = FormFieldName
        fields = ["field_name", "value", "fieldtype"]

    def get_fieldtype(self, obj):
        return obj.field_type.name


class ServiceSerializer(serializers.ModelSerializer):
    field = FormFieldNameSerializer(many=True)

    class Meta:
        model = Services
        fields = ["name", "id", "desc", "field", "parent", "image", "rate"]


class SerializerOrder(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Orders
        fields = ["service", "status", "eta"]


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyValue
        depth = 1
        fields = ["key", "value"]


class OrderSerializer(serializers.ModelSerializer):

    order_detail = OrderDetailSerializer(read_only=True, many=True)

    class Meta:
        model = Orders
        fields = ["service", "order_detail"]

    def validate(self, data):
        keys = []
        print(self.context.get("details"))
        for key in dict(self.context.get("details")):
            keys.append(key)

        print(FormFieldName.objects.filter(Service=self.context.get("service")))
        for field in FormFieldName.objects.filter(Service=self.context.get("service")):
            print(field.field_name)
            if field.field_name not in keys:
                raise serializers.ValidationError(f"{field.field_name} is required")
        return data

    def create(self, data):
        ordr = self.Meta.model.objects.create(
            user=self.context.get("request").user, service=self.context.get("service")
        )
        for key, value in self.context.get("details").items():
            KeyValue.objects.create(order=ordr, key=key, value=value)
        return data

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['message', 'title', 'image']
    
    