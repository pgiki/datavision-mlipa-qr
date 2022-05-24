from django.views.generic import DetailView, ListView, UpdateView, CreateView
from .models import App
from .forms import AppForm


class AppListView(ListView):
    model = App


class AppCreateView(CreateView):
    model = App
    form_class = AppForm


class AppDetailView(DetailView):
    model = App


class AppUpdateView(UpdateView):
    model = App
    form_class = AppForm

