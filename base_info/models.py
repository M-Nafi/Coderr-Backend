from django.db import models


class Review(models.Model):
    rating = models.FloatField()


class BusinessProfile(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)


class Offer(models.Model):
    title = models.CharField(max_length=100)
