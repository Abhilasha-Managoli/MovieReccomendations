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
    path('delete_from_watchlist/<int:movie_id>/', views.delete_from_watchlist, name='delete_from_watchlist'),
    path('delete_show_from_watchlist/<int:tv_id>/', views.delete_show_from_watchlist, name='delete_show_from_watchlist'),
    path('delete_from_favorites/<int:movie_id>/', views.delete_from_favorites, name='delete_from_favorites'),
    path('delete_show_from_favorites/<int:tv_id>/', views.delete_show_from_favorites, name='delete_show_from_favorites'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('popcornpicks/', views.popcornpicks_view, name='popcornpicks_view'),

]
