from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path("", views.home, name="home"),
    path("movie_recommendation/", views.movie_recommendation, name='movie_recommendation'),
    path("process_movie/", views.process_movie, name='process_movie'),
    path("logout/", views.logout_view, name='logout'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('userinfo/', views.userinfo_view, name='userinfo'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('add_to_favorites/', views.add_to_favorites, name="add_to_favorites"),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
