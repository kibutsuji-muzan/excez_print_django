from rest_framework import serializers
from exizprint.models.services import Services, FormFieldName, FormFieldType, Orders, KeyValue

class FieldTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FormFieldType
        fields= ['name']

class FormFieldNameSerializer(serializers.ModelSerializer):
    field_type = FieldTypeSerializer(many=False)
    class Meta:
        model = FormFieldName
        fields = ["field_name", "value", "field_type"]

class ServiceSerializer(serializers.ModelSerializer):
    field = FormFieldNameSerializer(many=True)
    class Meta:
        model = Services
        fields = ["name", "id",'desc', "field"]

class OrderSerializer(serializers.ModelSerializer):
    order_of = ServiceSerializer(read_only=True)
    class meta:
        model = Orders
        fields = ['order_of']