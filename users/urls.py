from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.home, name="home"),
    path("process_movie/", views.process_movie, name='process_movie'),
    path("logout/", views.logout_view, name='logout'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('userinfo/', views.userinfo_view, name='userinfo'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('add_to_favorites/', views.add_to_favorites, name="add_to_favorites"),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('remove_from_favorites/', views.remove_from_favorites, name='remove_from_favorites'),
    path('popcornpicks/', views.popcornpicks_view, name='popcornpicks_view'),

]
