from rest_framework import serializers
from exizprint.models.services import Services, FormFieldName, FormFieldType


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ["name", "id", "parent"]


class FormFieldNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFieldName
        fields = ["Service", "field_name", "value", "field_type"]
