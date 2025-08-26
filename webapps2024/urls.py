"""
URL configuration for webapps2024 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path

from payapp.views import notification_view
from register import views as register_views
from payapp import views as payapp_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', payapp_views.home, name="home"),
    path('', payapp_views.home, name="home"),
    path("register/", register_views.register_user, name="register"),
    path("login/", register_views.login_user, name="login"),
    path("logout/", register_views.logout_user, name="logout"),
    path("makepayment/", payapp_views.balance_transfer, name="balance_transfer"),
    path("requestpayment/", payapp_views.request_payment, name="request_payment"),
    path("conversion/<str:currency1>/<str:currency2>/<str:amount>/", payapp_views.CurrencyConversion.as_view(), name='convert_currency'),
    path('notifications/', notification_view, name='notifications'),
    path('processtransfer', payapp_views.process_request_payment, name='processtransfer'),
    path('transactions/', payapp_views.view_transactions, name='view_transactions')

]

