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
        """
        Return a string representation of the Review, in the format
        <reviewer> business_reviewer <business_user>.
        """
        return f"{self.reviewer} business_reviewer {self.business_user}"
    
    def update(self, *args, **kwargs):
        """
        Updates the Review instance and the updated_at field.

        This method sets the updated_at field to the current time 
        and saves the instance with any additional positional and 
        keyword arguments provided.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """

        self.updated_at = now()
        super().save(*args, **kwargs)