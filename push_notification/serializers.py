from . import models

from rest_framework import serializers


class AppSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.App
        fields = (
            'pk', 
            'name', 
            'user', #the owner of the app;
            'created', 
            'lastUpdated', 
            'fcmSettings', 
            'accessToken', 
        )


