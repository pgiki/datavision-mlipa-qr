import unittest
from django.urls import reverse
from django.test import Client
from .models import App
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType


def create_django_contrib_auth_models_user(**kwargs):
    defaults = {}
    defaults["username"] = "username"
    defaults["email"] = "username@tempurl.com"
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_django_contrib_auth_models_group(**kwargs):
    defaults = {}
    defaults["name"] = "group"
    defaults.update(**kwargs)
    return Group.objects.create(**defaults)


def create_django_contrib_contenttypes_models_contenttype(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ContentType.objects.create(**defaults)


def create_app(**kwargs):
    defaults = {}
    defaults["name"] = "name"
    defaults["fcmSettings"] = "fcmSettings"
    defaults["accessToken"] = "accessToken"
    defaults.update(**kwargs)
    if "user" not in defaults:
        defaults["user"] = create_django_contrib_auth_models_user()
    return App.objects.create(**defaults)


class AppViewTest(unittest.TestCase):
    '''
    Tests for App
    '''
    def setUp(self):
        self.client = Client()

    def test_list_app(self):
        url = reverse('push_notification_app_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_app(self):
        url = reverse('push_notification_app_create')
        data = {
            "name": "name",
            "fcmSettings": "fcmSettings",
            "accessToken": "accessToken",
            "user": create_django_contrib_auth_models_user().pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_detail_app(self):
        app = create_app()
        url = reverse('push_notification_app_detail', args=[app.pk,])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_app(self):
        app = create_app()
        data = {
            "name": "name",
            "fcmSettings": "fcmSettings",
            "accessToken": "accessToken",
            "user": create_django_contrib_auth_models_user().pk,
        }
        url = reverse('push_notification_app_update', args=[app.pk,])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)


