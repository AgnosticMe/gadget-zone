from django.contrib import admin
from .models import Product

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'category', 'is_available' , 'stock', 'date_modified' ]
    prepopulated_fields = {'slug': ('product_name',)}
    ordering = ['-date_created']