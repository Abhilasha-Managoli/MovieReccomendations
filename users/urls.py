from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path("", views.home, name="sign_in"),
    path("logout", views.logout_view)
]
