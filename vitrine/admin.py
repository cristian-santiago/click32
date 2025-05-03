from django.contrib import admin
from .models import Store

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'highlight')
    search_fields = ('name',)
    list_filter = ('highlight',)