from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction as db_transaction

from .models import Transaction, Product


@receiver(post_save, sender=Transaction)
def update_product_stock(sender, instance, created, **kwargs):
    if not created:
        return

    product = instance.product

    with db_transaction.atomic():
        product.stock -= instance.amount

        if product.stock <= 0:
            product.stock = 0
            product.status = Product.STATUS_OUT_OF_STOCK
        else:
            if product.status == Product.STATUS_OUT_OF_STOCK:
                product.status = Product.STATUS_AVAILABLE

        product.save()