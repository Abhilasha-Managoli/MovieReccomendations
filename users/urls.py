from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path("", views.home, name="home"),
    path("movie_recommendation/", views.movie_recommendation, name='movie_recommendation'),
    path("process_movie/", views.process_movie, name='process_movie'),
    path("logout/", views.logout_view, name='logout')
]
