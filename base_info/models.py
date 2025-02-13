from django.db import models


class Review(models.Model):
    rating = models.FloatField()
