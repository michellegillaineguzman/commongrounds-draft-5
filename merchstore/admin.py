from django.contrib import admin

from .models import Product, ProductType, Transaction


class ProductTypeAdmin(admin.ModelAdmin):
    model = ProductType


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'product_type', 'owner', 'price', 'stock', 'status')
    list_filter = ('product_type', 'status')
    search_fields = ('name',)


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = ('product', 'buyer', 'amount', 'status', 'created_on')
    list_filter = ('status',)


admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Transaction, TransactionAdmin)