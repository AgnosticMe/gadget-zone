from django.db import models
from django.urls import reverse
from category.models import Category
from accounts.models import Account

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='images/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    

    def get_url(self):
        return reverse('store:product_details', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name



class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'Product Gallery'
        verbose_name_plural = 'Product Gallery'


class VariationManager(models.Manager):
    def all(self):
        return super(VariationManager, self).filter(is_active=True)
    
    def color(self):
        return self.all().filter(variation_category='color')
    
    def size(self):
        return self.all().filter(variation_category='size')

    def style_name(self):
        return self.all().filter(variation_category='style name')

    def pattern_name(self):
        return self.all().filter(variation_category='pattern name')



variants_choices = (
    ('color', 'color'),
    ('size', 'size'),
    ('style name', 'style name'),
    ('pattern name', 'pattern name'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=255, choices=variants_choices)
    variation_value = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


    
class ReviewAndRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

