__author__ = 'kaushal'

from django.conf.urls import url
from .views import AccountsAPI, PaymentAPI

urlpatterns = [
    url(r'^accounts/$', AccountsAPI.as_view()),
    url(r'^payments/$', PaymentAPI.as_view()),
]
