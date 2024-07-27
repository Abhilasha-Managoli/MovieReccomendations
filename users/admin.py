from django.contrib import admin
from .models import Wishlist, Favorites


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie_title')
    search_fields = ('user__username', 'movie_title')


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie_title')
    search_fields = ('user__username', 'movie_title')
