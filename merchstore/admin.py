from django.contrib import admin
from .models import ProductType, Product


class ProductTypeAdmin(admin.ModelAdmin):
    model = ProductType


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'product_type', 'price')
    list_filter = ('product_type',)
    search_fields = ('name',)


admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)