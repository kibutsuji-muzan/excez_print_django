from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins

from exizprint.serializers.service_serializer import ServiceSerializer
from exizprint.models.services import Services

class ServiceView(mixins.RetrieveModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    http_method_names = ["get"]
    serializer_class = ServiceSerializer
    queryset = Services.objects.filter(parent=None)

    def retrieve(self, request, pk):
        ser = Services.objects.filter(parent=pk)
        print(len(ser))
        if len(ser):
            serializer = self.serializer_class(ser,many=True)
            print(serializer.data)
            return Response(serializer.data)
        return Response("No Service Found", status=status.HTTP_404_NOT_FOUNDs)

    def list(self, request):
        print(self.queryset)
        return super().list(request)