from django.urls import path

from . import views

app_name = 'merchstore'

urlpatterns = [
    path('items', views.ProductListView.as_view(), name='product-list'),
    path('item/add', views.product_create, name='product-create'),
    path('item/<int:pk>', views.ProductDetailView.as_view(), name='product-detail'),
    path('item/<int:pk>/edit', views.product_update, name='product-update'),
    path('cart', views.cart, name='cart'),
    path('cart/remove/<int:pk>', views.remove_from_cart, name='cart-remove'),
    path('transactions', views.transaction_list, name='transactions'),
]