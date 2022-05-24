from __future__ import absolute_import

from . import models
from . import serializers
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model

#rest framework
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

# for push notification
from rest_framework import permissions
from rest_framework.serializers import ModelSerializer, ValidationError, \
    Serializer, CurrentUserDefault
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from fcm_django.models import FCMDevice
from django import VERSION as DJ_VERSION
from django.db.models import Q
from fcm_django.settings import FCM_DJANGO_SETTINGS as SETTINGS

from django.contrib.auth import authenticate, login
User=get_user_model()

# Django 2 and 1 compatibility layer
def is_user_authenticated(user):
    """ Django 2 and 1 compatibility layer.

    Arguments:
    user -- Django User model.
    """

    if DJ_VERSION[0] > 1:
        return user.is_authenticated
    else:
        return user.is_authenticated()


# Serializers
class DeviceSerializerMixin(ModelSerializer):
    class Meta:
        fields = (
            "id", "name", "registration_id", "device_id", "active",
            "date_created", "type"
        )
        read_only_fields = ("date_created",)

        extra_kwargs = {"active": {"default": True}}


class UniqueRegistrationSerializerMixin(Serializer):
    
    def validate(self, attrs):
        devices = None
        primary_key = None
        request_method = None

        if self.initial_data.get("registration_id", None):
            if self.instance:
                request_method = "update"
                primary_key = self.instance.id
            else:
                request_method = "create"
        else:
            if self.context["request"].method in ["PUT", "PATCH"]:
                request_method = "update"
                primary_key = attrs["id"]
            elif self.context["request"].method == "POST":
                request_method = "create"

        Device = self.Meta.model
        # if request authenticated, unique together with registration_id and
        # user
        user = self.context['request'].user
        if request_method == "update":
            if user is not None and is_user_authenticated(user):
                devices = Device.objects.filter(
                    registration_id=attrs["registration_id"]) \
                    .exclude(id=primary_key)
                if attrs.get('active', False):
                    devices.filter(~Q(user=user)).update(active=False)
                devices = devices.filter(user=user)
            else:
                devices = Device.objects.filter(
                    registration_id=attrs["registration_id"]) \
                    .exclude(id=primary_key)
       
        elif request_method == "create":
            if user is not None and is_user_authenticated(user):
                devices = Device.objects.filter(
                    registration_id=attrs["registration_id"])
                devices.filter(~Q(user=user)).update(active=False)
                devices = devices.filter(user=user, active=True)
            else:
                devices = Device.objects.filter(
                    registration_id=attrs["registration_id"])

        if devices:
            raise ValidationError(
                {'registration_id': 'This field must be unique.'})
        return attrs


class FCMDeviceSerializer(ModelSerializer, UniqueRegistrationSerializerMixin):
    class Meta(DeviceSerializerMixin.Meta):
        model = FCMDevice

        extra_kwargs = {"id": {"read_only": True, "required": False}}
        extra_kwargs.update(DeviceSerializerMixin.Meta.extra_kwargs)


# Permissions
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # must be the owner to view the object
        return obj.user == request.user


# Mixins
class DeviceViewSetMixin(object):
    lookup_field = "registration_id"
    app=None

    def login_user(self):
        if not is_user_authenticated(self.request.user):
            data=self.request.data
            app=data.get("app")
            username=data.get("username")
            accessToken=data.get("accessToken")
            # print("app", app, "username", username) 
            #first check in if valid access token was provided to verify the user accessing the service
            #if the app is valid
            try:
                self.app=models.App.objects.get(name=app, accessToken=accessToken);
                # if username not provided then just intended to push notification, hence login the app owner
                if not username:
                    login(self.request, self.app.user)

            except Exception as e:
                return

            if app and username:
                #login if user does not exist
                if self.app:
                    user, created=User.objects.get_or_create(username=f"{username}_{app}")
                    if created:
                        #set default password for that user
                        user.set_password(username)
                    #now login the user
                    login(self.request, user)
                    # print("User is just logged in", self.request.user)
                else:
                    # print("Not valid access token ", app, "accessToken", accessToken)
                    pass
            else:
                # print("app and/or username not provided")
                pass

        else:
            # print("User is authenticated")
            pass
            
    def perform_create(self, serializer):
        self.login_user()
        if is_user_authenticated(self.request.user):
            if (SETTINGS["ONE_DEVICE_PER_USER"] and
                    self.request.data.get('active', True)):
                FCMDevice.objects.filter(user=self.request.user).update(
                    active=False)
            return serializer.save(user=self.request.user)
        return serializer.save()

    def perform_update(self, serializer):
        self.login_user()
        if is_user_authenticated(self.request.user):
            if (SETTINGS["ONE_DEVICE_PER_USER"] and
                    self.request.data.get('active', False)):
                FCMDevice.objects.filter(user=self.request.user).update(
                    active=False)

            return serializer.save(user=self.request.user)
        return serializer.save()


class AuthorizedMixin(object):
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    def get_queryset(self):
        # filter all devices to only those belonging to the current user
        return self.queryset.filter(user=self.request.user)

# ViewSets
class FCMDeviceViewSet(DeviceViewSetMixin, ModelViewSet):
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = (permissions.AllowAny,)

    @action(detail=False, methods=['POST', "GET"], name='Send Notifications to devices', url_path='push')
    def push(self, request, *args, **kwargs):
        """
        SAMPLE
            {
               "app":"com.mlipa.payments",
               "accessToken":"6ae49be6-c56b-42e5-b7e0-b8b13d4b9e76",
               "username":"user requesting service",
               "messages":[
                  {
                     "users":[
                        "user1",
                        "user2"
                     ],
                     "message":{
                        "title":"Title",
                        "body":"Body of the message"
                     }
                  },

                  {
                     "users":[
                        "user1",
                        "user2"
                     ],
                     "message":{
                        "title":"Title",
                        "body":"Body of the message"
                     }
                  }
               ]
            }
        """
        results={"status": 406}
        devicesCount=0
        data=request.data

        #step1: First authenticate the user by verifying their access token
        self.login_user()
        if not self.request.user.is_authenticated:
            results.update({"detail":"Invalid credential. Please verify your access token and app name"})
       
        elif self.app:
            messages=data.get("messages", [])
            app=data.get("app")
            api_key=self.app.fcmSettings.get("FCM_SERVER_KEY")

            for message in messages:
                receivers=message.get("users", [])
                #append the app name on the users username
                receivers=[f"{receiver}_{app}" for receiver in receivers ]
                devices = FCMDevice.objects.filter(user__username__in=receivers)
                #append API_KEY to the message if provided
                if api_key:
                    message.update({"api_key":api_key})
                devices.send_message(**message)
                devicesCount=devicesCount+devices.count()
                # devices.send_message(title="Title", body="Message", data={"test": "test"})
                # devices.send_message(data={"test": "test"})
        else:
           results.update({"detail":"Invalid access token and/or app name"})
        results.update({"count":devicesCount})
        return Response(results)


class FCMDeviceCreateOnlyViewSet(DeviceViewSetMixin, CreateModelMixin, GenericViewSet):
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer

class FCMDeviceAuthorizedViewSet(AuthorizedMixin, FCMDeviceViewSet):
    pass


class AppViewSet(viewsets.ModelViewSet):
    """ViewSet for the App class"""
    queryset = models.App.objects.all().order_by("id")
    serializer_class = serializers.AppSerializer
    permission_classes = [permissions.IsAuthenticated]


