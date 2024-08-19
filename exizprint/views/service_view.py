import json
import random
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from django.shortcuts import render
from django.views import View
from rest_framework.renderers import TemplateHTMLRenderer
from exizprint.serializers.service_serializer import (
    PaymentSerializer,
    ServiceSerializer,
    OrderSerializer,
    SerializerOrder,
    BannerSerializer,CheckoutSerializer
)
from exizprint.models.services import (
    Services,
    Orders,
    Banner,
    FormFieldName,
    PaymentModel,CheckOut
)
from accounts.models.UserModel import User, default_key
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
import os
import razorpay.client
import core.settings as setting
from core.task import SendMail


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
        print(os.environ["PATH"])

        return super().list(request)

    @action(methods=["get"], detail=False, url_name="get_banner", url_path="get-banner")
    def getbanner(self, request):
        serializer = BannerSerializer(Banner.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False, url_name="search", url_path="search")
    def search(self, request):
        query = []
        for q in Services.objects.filter(
            name__contains=str(request.META.get("QUERY_STRING")).title().split("=")[1]
        ):
            if q.parent != None:
                query.append(q)

        serializer = ServiceSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrdersView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    http_method_names = ["get", "post"]
    # permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def list(self, request):
        queryset = Orders.objects.filter(user=request.user)
        serializer = SerializerOrder(queryset, many=True)
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
        except:
            return Response("Service Is Required")
        sorted(service.price.all(), key=lambda price: price.above)
        fields = {}
        files = {}
        id = {}
        for key in request.data:
            if key != "service":
                fields[key] = request.data[key]

        serializer = OrderSerializer(
            data=request.data,
            context={
                "request": request,
                "service": service,
                "fields": fields,
                "files": files,
                "id": id,
            },
        )
        if serializer.is_valid(raise_exception=True):
            serializer.create(serializer.data)
            maildata = {
                "mail": "init-service",
                "email": request.user.email,
                "priority": "now",
            }
            SendMail.delay(maildata)
            return Response(
                {
                    "response": "Your Order Has Been Placed",
                    "id": id.get("id"),
                    "data": serializer.data,
                }
            )
        return Response("something went wrong", status=status.HTTP_400_BAD_REQUEST)

    # @action(
    #     methods=["get"],
    #     detail=True,
    #     url_name="create_checkout",
    #     url_path="create-checkout",
    # )
    # def createCheckout(self, request):
    #     serializer = CheckoutSerializer(data = request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.create()
    #         return Response("Checkout Created")
    #     return Response("somethig went wrong", status=status.HTTP_400_BAD_REQUEST)


class CheckoutView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
    ):
    http_method_names = ["get", "post", "delete"]
    permission_classes = [IsAuthenticated]

    def list(self,request):
        query = CheckOut.objects.filter(user=request.user, active = True)
        serializer = CheckoutSerializer(query, many=True)
        return Response(serializer.data)

    def create(self, request):
        try:
            ordr = Orders.objects.get(id=request.data.get('order_id'))
        except:
            return Response('No order found', status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        serializer = CheckoutSerializer(data=data)
        if(serializer.is_valid(raise_exception=True)):
            checkout = serializer.create(serializer.data)
            print(checkout.id)
            checkout.user  =request.user
            checkout.save()
            ordr.checkout = checkout
            return Response("Checkout data saved")
        return Response("Something went wrong")
        
    @action(
        methods=["post"],
        detail=False,
        url_name="set_checkout",
        url_path="set-checkout",
    )
    def setcheckout(self, request, pk):
        try:
            co = CheckOut.objects.get(id=pk)
            ordr = Orders.objects.get(id=request.data.get('order_id'))
        except:
            return Response('object not found', status=status.HTTP_400_BAD_REQUEST)
        ordr.checkout = co
        ordr.save()
        return Response('checkout success')
        
    @action(
        methods=["delete"],
        detail=True,
        url_name="delete_checkout",
        url_path="delete-checkout",
    )
    def delete(self, request):
        try:
            co = CheckOut.objects.get(id=request.data.get('checkout_id'))
        except:
            return Response('object not found', status=status.HTTP_400_BAD_REQUEST)
        co.active = False
        co.save()
        return Response('checkout deleted success')


class PaymentPortal(viewsets.GenericViewSet):
    http_method_names = ["get", "post"]
    permission_classes = [IsAuthenticated]

    @action(
        methods=["get"],
        detail=True,
        url_name="create_payment_order",
        url_path="create-payment-order",
    )
    def createOrder(self, request, pk):
        try:
            order = Orders.objects.get(id=pk)
        except:
            return Response("something went wrong", status=status.HTTP_400_BAD_REQUEST)
        service = order.service
        if order.status == "unpaid":
            client = razorpay.Client(auth=(setting.p_key, setting.s_key))
            data = {
                "amount": order.bill * 100,
                "currency": "INR",
                "receipt": default_key(20),
            }
            payment = client.order.create(data=data)
            return Response(
                {
                    "order": order.id,
                    "payment": {
                        "key": setting.p_key,
                        "amount": payment.get("amount"),
                        "name": service.name,
                        "order_id": payment.get("id"),
                        # "description": "Fine T-Shirt",
                        "timeout": 60 * 15,
                        "prefill": {
                            "email": request.user.email,
                        },
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response("Already Paid Order", status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["post"],
        detail=True,
        url_name="verify_payment_order",
        url_path="verify-payment-order",
    )
    def verifyOrder(self, request, pk):
        try:
            order = Orders.objects.get(id=pk)
        except:
            return Response("something went wrong", status=status.HTTP_400_BAD_REQUEST)
        client = razorpay.Client(auth=(setting.p_key, setting.s_key))
        serializer = PaymentSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            payment = PaymentModel.objects.create(
                razorpay_order_id=request.data.get("razorpay_order_id"),
                razorpay_payment_id=request.data.get("razorpay_payment_id"),
                razorpay_signature=request.data.get("razorpay_signature"),
                ordr=order,
            )
            valid = client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": payment.razorpay_order_id,
                    "razorpay_payment_id": payment.razorpay_payment_id,
                    "razorpay_signature": payment.razorpay_signature,
                }
            )
            if valid:
                order.status = "paid"
                order.payment_status = True
                order.save()
                return Response("Successfull Payment", status=status.HTTP_200_OK)
            return Response("Signature Not Valid", status=status.HTTP_400_BAD_REQUEST)
        return Response("Already Paid Order", status=status.HTTP_400_BAD_REQUEST)


class PrivacyPolicy(viewsets.GenericViewSet):
    renderer_classes = [TemplateHTMLRenderer]

    @action(
        methods=["get"],
        detail=False,
        url_name="policy",
        url_path="policy",
    )
    def privacypolicy(self, request, *args, **kwargs):
        return Response(template_name="PrivacyPolicy.html")

    @action(
        methods=["get"],
        detail=False,
        url_name="terms",
        url_path="terms",
    )
    def termscondition(self, request, *args, **kwargs):
        return Response(template_name="TermsAndCondition.html")

    @action(
        methods=["get"],
        detail=False,
        url_name="donate",
        url_path="donate",
    )
    def donation(self, request, *args, **kwargs):
        return Response(template_name="SupportUs.html")
