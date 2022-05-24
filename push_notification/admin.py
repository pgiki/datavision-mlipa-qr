from django.contrib import admin
from django import forms
from .models import App

class AppAdminForm(forms.ModelForm):

    class Meta:
        model = App
        fields = '__all__'


class AppAdmin(admin.ModelAdmin):
    form = AppAdminForm
    list_display = ['name', 'created', 'lastUpdated', 'fcmSettings', 'accessToken']
    # readonly_fields = ['name', 'created', 'lastUpdated', 'fcmSettings', 'accessToken']

admin.site.register(App, AppAdmin)


