from django.contrib import admin
from .models import *

@admin.register(Adminprofile)
class AdminprofileAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact', 'address', 'regdate')
    search_fields = ('user__username',)
    list_filter = ('regdate',)

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('user','contact', 'address', 'regdate')
    search_fields = ('user__username', 'contact','address')
    list_filter = ('regdate',)

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'donation_type', 'collection_address', 'submitted_at')
    search_fields = ('donor__username', 'donation_type', 'collection_address')
    list_filter = ('submitted_at',)

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact', 'address', 'regdate')
    search_fields = ('user__username',)
    list_filter = ('regdate',)

@admin.register(DonationArea)
class DonationAreaAdmin(admin.ModelAdmin):
    list_display = ('areaname', 'description', 'creationdate')
    search_fields = ('areaname', 'description')
    list_filter = ('creationdate',)
    
admin.site.register(Beneficiary)