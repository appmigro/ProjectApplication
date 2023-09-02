from django.urls import path
from LoggingApp import views

app_name = "LoggingApp"

urlpatterns = [
    path("", views.login_view, name="login_view"),
]