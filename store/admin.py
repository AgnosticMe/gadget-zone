from django.contrib import admin
from .models import Product, ProductGallery


class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'category', 'is_available' , 'stock', 'date_modified' ]
    prepopulated_fields = {'slug': ('product_name',)}
    ordering = ['-date_created']
    inlines = [ProductGalleryInline]



admin.site.register(ProductGallery)



