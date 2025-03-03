from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('business_user', 'reviewer', 'rating', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at', 'updated_at')
    search_fields = ('business_user__username', 'reviewer__username')

admin.site.register(Review, ReviewAdmin)