from django.db import models
from django.urls import reverse

from accounts.models import Profile


class ProductType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_AVAILABLE = 'Available'
    STATUS_ON_SALE = 'On sale'
    STATUS_OUT_OF_STOCK = 'Out of stock'

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_ON_SALE, 'On sale'),
        (STATUS_OUT_OF_STOCK, 'Out of stock'),
    ]

    name = models.CharField(max_length=255)
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        blank=True,
    )
    product_image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('merchstore:product-detail', args=[str(self.pk)])


class Transaction(models.Model):
    STATUS_ON_CART = 'On cart'
    STATUS_TO_PAY = 'To Pay'
    STATUS_TO_SHIP = 'To Ship'
    STATUS_TO_RECEIVE = 'To Receive'
    STATUS_DELIVERED = 'Delivered'

    STATUS_CHOICES = [
        (STATUS_ON_CART, 'On cart'),
        (STATUS_TO_PAY, 'To Pay'),
        (STATUS_TO_SHIP, 'To Ship'),
        (STATUS_TO_RECEIVE, 'To Receive'),
        (STATUS_DELIVERED, 'Delivered'),
    ]

    buyer = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='buyer_transactions',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ON_CART)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f'{self.buyer} - {self.product} x{self.amount}'