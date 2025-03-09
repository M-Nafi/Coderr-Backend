from django.db import models  
from django.contrib.auth.models import User  

class Offer(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    title = models.CharField(max_length=255)  
    description = models.TextField()  
    image = models.FileField(upload_to='uploads/', null=True) 
    updated_at = models.DateTimeField(auto_now=True)  
    created_at = models.DateTimeField(auto_now_add=True)  

class OfferDetail(models.Model):  
    OFFER_TYPES = [('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')]  

    title = models.CharField(max_length=255)  
    price = models.FloatField(default=1)  
    delivery_time_in_days = models.IntegerField(default=1)  
    offer = models.ForeignKey(Offer, related_name='details', on_delete=models.CASCADE)  
    features = models.JSONField()  
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPES)  
    revisions = models.IntegerField(default=-1)  

    def round_price(self): 
        """
        Rounds the price of the offer detail to two decimal places.
        This method ensures that the price attribute is rounded to two decimal places
        if it is not None.
        """
        if self.price is not None:  
            self.price = round(self.price, 2)  

    def save(self, *args, **kwargs): 
        """
        Saves the offer detail instance to the database.
        This method is overridden to round the price of the offer detail to two decimal
        places before saving it to the database.
        """
        self.round_price() 
        super().save(*args, **kwargs) 

