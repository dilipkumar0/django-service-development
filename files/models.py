from django.contrib.auth.models import Permission, User
from django.db import models


class Album(models.Model):
    user = models.ForeignKey(User, default=1)
    artist = models.CharField(max_length=250)
    album_title = models.CharField(max_length=500)
    genre = models.CharField(max_length=100)
    album_logo = models.FileField(upload_to='media')
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.album_title + ' - ' + self.artist


class Images(models.Model):
    album = models.ForeignKey(Album,related_name='image_set',on_delete=models.CASCADE)
    image_title = models.CharField(max_length=250)
    image_file = models.FileField(upload_to='media')
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.image_title
