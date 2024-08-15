"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from accounts.views.AccountsView import AccountsManagement, PasswordRest
from exizprint.views.service_view import ServiceView, OrdersView, PaymentPortal, PrivacyPolicy

router = DefaultRouter()

router.register(r'services', ServiceView, basename='services')
router.register(r'orders', OrdersView, basename='orders')
router.register(r'accounts', AccountsManagement, basename='accounts')
router.register(r'payment', PaymentPortal, basename='payment')
router.register(r'p', PrivacyPolicy, basename='privacy')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/<token>/password-reset', PasswordRest.as_view()),
    # path('test', testview),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += router.urls
