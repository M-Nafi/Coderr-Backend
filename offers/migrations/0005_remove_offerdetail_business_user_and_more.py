# Generated by Django 5.1.5 on 2025-03-16 13:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offers', '0004_offerdetail_business_user_offerdetail_customer_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offerdetail',
            name='business_user',
        ),
        migrations.RemoveField(
            model_name='offerdetail',
            name='customer_user',
        ),
    ]
