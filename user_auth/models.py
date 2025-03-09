from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email = models.EmailField(unique=True, error_messages={'unique': "Email existiert bereits."})
    username = models.CharField(max_length=150, default='Nutzername')
    first_name = models.CharField(max_length=100, default = 'Aktualisiere deinen Namen')
    last_name = models.CharField(max_length=100, default='Aktualisiere deinen Nachnamen')
    type = models.CharField(max_length=100, choices=[('business', 'business'), ('customer', 'customer')])
    tel = models.CharField(max_length=100, default = '0123456789')
    location = models.CharField(max_length=100, default = 'location')
    description = models.TextField(max_length=1000, default = '')
    file = models.FileField(blank=True, null=True, upload_to='uploads/')
    working_hours = models.CharField(max_length=100, default = '09:00 - 18:00')
    uploaded_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    
    def save(self, *args, **kwargs):
        """
        Saves the Profile instance.

        This method updates the username field with the user's username before saving.
        If the profile already exists (i.e., has a primary key), it checks if the file field
        has been changed. If the file has changed, the uploaded_at field is updated to the
        current time. Finally, it calls the superclass's save method to save the instance.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """

        self.username = self.user.username
        
        if self.pk:  
            original = Profile.objects.get(pk=self.pk)
            if original.file != self.file:  
                self.uploaded_at = now()
        super().save(*args, **kwargs)
 
    def __str__(self):
        """
        Returns a string representation of the Profile instance.

        The string representation includes the username of the associated
        User instance and the value of the type field.

        :return: A string representation of the Profile instance.
        """
        return f"{self.user.username} - {self.type}"
