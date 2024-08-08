from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_title = models.CharField(max_length=255, null=True, blank=True)
    show_title = models.CharField(max_length=255, null=True, blank=True)
    movie_id = models.IntegerField(null=True, blank=True)
    tv_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.movie_title or self.show_title or f"Wishlist item for {self.user}"


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_title = models.CharField(max_length=255, null=True, blank=True)
    show_title = models.CharField(max_length=255, null=True, blank=True)
    movie_id = models.IntegerField(null=True, blank=True)
    tv_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.movie_title or self.show_title or f"Favorite item for {self.user}"

    class Meta:
        verbose_name_plural = "Favorites"
