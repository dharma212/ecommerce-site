from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Order, OrderItem
from cart.models import Cart
from product.models import *
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('cart_list')

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
        })

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('cart_list')

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        address = request.POST.get('address') or request.user.address
        phone = request.POST.get('phone') or request.user.contact_number
        payment_method = request.POST.get('payment_method', 'COD')

        order = Order.objects.create(
            user=request.user,
            full_name=request.user.get_full_name(),
            address=address,
            phone=phone,
            total_price=total_price,
            payment_method=payment_method
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        Cart.objects.filter(user=request.user).delete()

        return render(request, 'order_success.html', {'order': order})

class MyOrdersView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'order.html', {'orders': orders}) 

class PaymentView(LoginRequiredMixin, View):
    template_name = 'payment.html'

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('cart')

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        return render(request, self.template_name, {
            'total_price': total_price,
        })

    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('cart')

        payment_method = request.POST.get('payment_method', 'COD')
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=request.user,
            full_name=request.user.get_full_name(),
            address=request.user.address,
            phone=request.user.contact_number,
            total_price=total_price,
            payment_method=payment_method,
            status='Pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        Cart.objects.filter(user=request.user).delete()

        # ✅ IMPORTANT: redirect to order detail
        return redirect('order_detail', order_id=order.id)
     
class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return render(request, 'order_detail.html', {'order': order})

def get_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return JsonResponse({'status': order.status})
   