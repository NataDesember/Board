from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Category(models.Model):
    category_name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.category_name


class Announce(models.Model):
    time_in = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Feedback(models.Model):
    announce = models.ForeignKey(Announce, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    time_in = models.DateTimeField(auto_now_add=True)
