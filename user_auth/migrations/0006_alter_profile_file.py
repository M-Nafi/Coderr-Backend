# Generated by Django 5.1.5 on 2025-02-10 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0005_alter_profile_email_alter_profile_first_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]
