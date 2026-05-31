import importlib

from django.conf import settings
from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView

views = importlib.import_module(settings.MODELS_MODULE + ".views")

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("units")), name="homepage"),
    path("units/", views.UnitListView.as_view(), name="units"),
    path("units/<int:page>/", views.UnitListView.as_view(), name="units_page"),
]
