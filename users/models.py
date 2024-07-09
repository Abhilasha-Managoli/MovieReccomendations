from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_title = models.CharField(max_length=255)

    def __str__(self):
        return self.movie_title
