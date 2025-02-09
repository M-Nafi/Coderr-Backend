from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email = models.EmailField(unique=True, error_messages={'unique': "Email existiert bereits."})
    username = models.CharField(max_length=150, default='Your Name')
    first_name = models.CharField(max_length=100, default = 'First Name')
    last_name = models.CharField(max_length=100, default='Last Name')
    type = models.CharField(max_length=100, choices=[('business', 'business'), ('customer', 'customer')])
    tel = models.CharField(max_length=100, default = '0123456789')
    location = models.CharField(max_length=100, default = 'location')
    description = models.TextField(max_length=1000, default = '')
    file = models.FileField(blank=True, null=True, upload_to='uploads/')
    working_hours = models.CharField(max_length=100, default = '09:00 - 18:00')
    uploaded_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.username = self.user.username
        
        if self.pk:  
            original = Profile.objects.get(pk=self.pk)
            if original.file != self.file:  
                self.uploaded_at = now()
        super().save(*args, **kwargs)
 
    def __str__(self):
        return f"{self.user.username} - {self.type}"
