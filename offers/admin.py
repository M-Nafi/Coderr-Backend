from django.contrib import admin  
from .models import Offer, OfferDetail  


class OfferDetailInline(admin.TabularInline):  
    model = OfferDetail 
    extra = 0  

@admin.register(Offer)  
class OfferAdmin(admin.ModelAdmin):  
    list_display = ('user', 'title', 'created_at', 'updated_at')  
    search_fields = ('user__username', 'title')  
    list_filter = ('created_at', 'updated_at')  
    inlines = [OfferDetailInline]  


@admin.register(OfferDetail)  
class OfferDetailAdmin(admin.ModelAdmin):  
    list_display = ('offer', 'offer_type', 'title', 'price')  
    search_fields = ('title', 'offer__title') 
    list_filter = ('price', 'offer_type') 
