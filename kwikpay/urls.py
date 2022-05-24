from django.urls import path, include
from rest_framework import routers
from . import api
urlpatterns = (
    # urls for Django Rest Framework API
    path('qr', api.generateQR, name='generateQR'),
    path('qr/', api.generateQR, name='generateQR'),
    path('weddingcard/', api.weddingCard, name='weddingCard'),
)




