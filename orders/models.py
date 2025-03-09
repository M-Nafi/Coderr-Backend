from django.db import models

from django.contrib.auth.models import User
from django.utils.timezone import now

class Order(models.Model):
    order_status = [
        ('in_progress', 'In Bearbeitung'),
        ('completed', 'Abgeschlossen'),
        ('cancelled', 'Abgebrochen')
    ]
    status = models.CharField(max_length=20, choices=order_status, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    offer_type = models.CharField(max_length=50, blank=True)
    offer_detail_id = models.ForeignKey('offers.OfferDetail', on_delete=models.CASCADE, verbose_name=("OfferDetail"))
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_time_in_days = models.IntegerField(null=True, blank=True)
    features = models.JSONField(null=True, blank=True)
    revisions = models.IntegerField(null=True, blank=True)
    customer_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=('Customer User'))
    business_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders_as_business", verbose_name=('Business User'))

    def save(self, *args, **kwargs):
        """
        Custom save method for orders.

        If the business user is not set when saving the order, it is set to the user of the offer detail.
        If the offer detail is set when saving the order, the title, revisions, delivery time in days, price, and features are set to the values of the offer detail if they are not set.
        """
        if not self.business_user_id and self.offer_detail_id:
            self.business_user = self.offer_detail_id.offer.user

        if self.offer_detail_id:
            self.title = self.title or self.offer_detail_id.title
            self.revisions = self.revisions if self.revisions is not None else self.offer_detail_id.revisions
            self.delivery_time_in_days = self.delivery_time_in_days if self.delivery_time_in_days is not None else self.offer_detail_id.delivery_time_in_days
            self.price = self.price if self.price is not None else self.offer_detail_id.price
            self.features = self.features if self.features is not None else self.offer_detail_id.features
            self.offer_type = self.offer_type or self.offer_detail_id.offer_type
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Updates the order and updates the updated_at field.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        self.updated_at = now()
        super().save(*args, **kwargs)