from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from product.models import Product
from .models import Cart


class AddToCartView(LoginRequiredMixin, View):
    login_url = '/user/login/'  # redirect if not logged in

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        # Redirect to the cart list using namespaced URL
        return redirect('cart_list')


from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cart


class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'cart_list.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return Cart.objects.select_related('product').filter(
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_price = sum(
            item.product.price * item.quantity
            for item in context['cart_items']
        )

        context['total_price'] = total_price
        return context
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cart, Product

class AddToCartAjaxView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        product = Product.objects.get(id=product_id)

        cart, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )

        return JsonResponse({"success": True})
