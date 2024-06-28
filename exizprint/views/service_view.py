from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins

from exizprint.serializers.service_serializer import ServiceSerializer, OrderSerializer, SerializerOrder, BannerSerializer
from exizprint.models.services import Services, Orders, Banner
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
import os

class ServiceView(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    http_method_names = ["get"]
    serializer_class = ServiceSerializer
    queryset = Services.objects.filter(parent=None)

    def retrieve(self, request, pk):
        ser = Services.objects.filter(parent=pk)
        print(len(ser))
        if len(ser):
            serializer = self.serializer_class(ser, many=True)
            print(serializer.data)
            return Response(serializer.data)
        return Response("No Service Found", status=status.HTTP_404_NOT_FOUNDs)

    def list(self, request):
        print(self.queryset)
        print(os.environ['PATH'])

        return super().list(request)

    @action(methods=["get"], detail=False, url_name="get_banner", url_path="get-banner")
    def getbanner(self, request):
        serializer = BannerSerializer( Banner.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrdersView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    http_method_names = ["get", "post"]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def list(self, request):
        queryset = Orders.objects.filter(user=request.user)
        serializer = SerializerOrder(queryset,many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        ordr = Orders.objects.get(id=pk)
        if len(ordr):
            serializer = self.serializer_class(ordr, many=True)
            print(serializer.data)
            return Response(serializer.data)
        return Response("No Order Found", status=status.HTTP_404_NOT_FOUNDs)

    def create(self, request):
        try:
            service = Services.objects.get(id=request.data.get("service"))
            details = request.data.get("order_detail")
        except:
            return Response("Service Is Required")
        
        serializer = OrderSerializer(data=request.data, context={"request":request, "service":service, "details":details})
        if serializer.is_valid(raise_exception=True):
            print(serializer.data)
            serializer.create(serializer.data)
            return Response(
                {
                    "response": "Your Order Has Been Placed",
                    "data": serializer.data,
                }
            )