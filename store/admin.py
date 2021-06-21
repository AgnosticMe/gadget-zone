from django.contrib import admin
from .models import Product, ProductGallery, Variation
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

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ['product', 'variation_category', 'variation_value', 'is_active']
    list_editable = ['is_active']
    list_filter = ['product', 'variation_category', 'variation_value']
    ordering = ['-updated']



admin.site.register(ProductGallery)



