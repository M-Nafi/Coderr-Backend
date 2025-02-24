from django.db import models
from offers.models import Offer
from django.contrib.auth.models import User
from django.utils.timezone import now


class Review(models.Model):
    rating = models.IntegerField()
    reviewer = models.ForeignKey(User, related_name='reviewer', on_delete=models.CASCADE)
    business_user = models.ForeignKey(User, related_name='business_reviewer', on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reviewer} business_reviewer {self.business_user}"
    
    def update(self, *args, **kwargs):
        self.updated_at = now()
        super().save(*args, **kwargs)