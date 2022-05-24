from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import models as models
from django.conf import settings
import uuid


class App(models.Model):
    # Fields
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    lastUpdated = models.DateTimeField(auto_now=True, editable=False)
    fcmSettings = models.JSONField(default=dict)
    accessToken = models.TextField(default=uuid.uuid4, blank=True)
    # Relationship Fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="apps", null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('push_notification_app_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('push_notification_app_update', args=(self.pk,))


