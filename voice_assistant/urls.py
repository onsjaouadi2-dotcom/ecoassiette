from django.urls import path

from . import views

app_name = "voice_assistant"

urlpatterns = [
    path("", views.assistant, name="assistant"),
    path("message/", views.message, name="message"),
    path("effacer/", views.effacer, name="effacer"),
]
