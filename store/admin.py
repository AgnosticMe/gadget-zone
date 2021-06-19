from django.contrib import admin
from .models import Product, ProductGallery
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

@admin.register(Product)
@admin_thumbnails.thumbnail('images')
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'category', 'is_available' , 'stock', 'date_modified' ]
    prepopulated_fields = {'slug': ('product_name',)}
    ordering = ['-date_created']
    inlines = [ProductGalleryInline]



admin.site.register(ProductGallery)



