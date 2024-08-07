# Generated by Django 5.1.dev20240204083941 on 2024-08-06 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_favorites_movie_id_favorites_tv_id_wishlist_movie_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorites',
            name='show_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='show_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='favorites',
            name='movie_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='movie_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
