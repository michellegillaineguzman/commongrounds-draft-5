from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView

from accounts.mixins import RoleRequiredMixin

from .forms import ProductForm, TransactionForm
from .models import Product, Transaction
from .strategies import AuthenticatedPurchaseStrategy, GuestPurchaseStrategy


class ProductListView(ListView):
    model = Product
    template_name = 'merchstore/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.all()
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(owner=self.request.user.profile)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_products'] = Product.objects.filter(owner=self.request.user.profile)
        else:
            context['user_products'] = []
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'merchstore/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['form'] = TransactionForm()
        context['is_owner'] = (
            self.request.user.is_authenticated
            and self.request.user.profile == product.owner
        )
        context['can_buy'] = (
            self.request.user.is_authenticated
            and not context['is_owner']
            and product.stock > 0
        )
        return context

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = TransactionForm(request.POST)

        if form.is_valid():
            if request.user.is_authenticated:
                strategy = AuthenticatedPurchaseStrategy()
            else:
                strategy = GuestPurchaseStrategy()
            return strategy.execute(request, product, form)

        is_owner = request.user.is_authenticated and request.user.profile == product.owner
        return render(request, self.template_name, {
            'product': product,
            'form': form,
            'is_owner': is_owner,
            'can_buy': not is_owner and product.stock > 0,
        })


@login_required
def product_create(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'Market Seller':
        return redirect('permission_denied')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user.profile
            product.save()
            return redirect('merchstore:product-detail', pk=product.pk)
    else:
        form = ProductForm()

    return render(request, 'merchstore/product_create.html', {'form': form})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if not hasattr(request.user, 'profile') or request.user.profile.role != 'Market Seller':
        return redirect('permission_denied')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.owner = product.owner
            if updated.stock == 0:
                updated.status = Product.STATUS_OUT_OF_STOCK
            elif updated.status == Product.STATUS_OUT_OF_STOCK:
                updated.status = Product.STATUS_AVAILABLE
            updated.save()
            return redirect('merchstore:product-detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'merchstore/product_update.html', {'form': form, 'product': product})


@login_required
def cart(request):
    profile = request.user.profile

    # Complete any pending guest transaction after login
    pending = request.session.pop('pending_transaction', None)
    if pending:
        from .models import Product as P
        try:
            product = P.objects.get(pk=pending['product_id'])
            Transaction.objects.create(
                buyer=profile,
                product=product,
                amount=pending['amount'],
                status='On cart',
            )
        except P.DoesNotExist:
            pass

    transactions = Transaction.objects.filter(buyer=profile).select_related('product', 'product__owner')

    cart_by_owner = defaultdict(list)
    for t in transactions:
        cart_by_owner[t.product.owner].append(t)

    return render(request, 'merchstore/cart.html', {'cart_by_owner': dict(cart_by_owner)})


@login_required
def transaction_list(request):
    profile = request.user.profile

    transactions = Transaction.objects.filter(
        product__owner=profile
    ).select_related('buyer', 'product')

    transactions_by_buyer = defaultdict(list)
    for t in transactions:
        transactions_by_buyer[t.buyer].append(t)

    return render(request, 'merchstore/transaction_list.html', {
        'transactions_by_buyer': dict(transactions_by_buyer),
    })