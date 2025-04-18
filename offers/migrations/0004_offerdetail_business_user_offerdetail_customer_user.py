# Generated by Django 5.1.5 on 2025-03-16 13:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0003_alter_offer_title_offerdetail_delete_offerdetails'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='offerdetail',
            name='business_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offers_as_business', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='offerdetail',
            name='customer_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offers_as_customer', to=settings.AUTH_USER_MODEL),
        ),
    ]
