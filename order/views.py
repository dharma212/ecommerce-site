from django.views import View
from django.views.generic import CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import date
from openpyxl import Workbook
from cart.models import Cart, Coupon, CouponUsage
from product.models import Product
from order.models import Order, OrderItem, CancelledOrder, Invoice
from .models import Feedback
from .forms import FeedbackForm
from .utils import generate_invoice

class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):
        buy_now_id = request.GET.get('buy_now')

        # ================= BUY NOW =================
        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)

            total_mrp = product.discount if product.discount else product.price
            total_price = product.price

            # ❌ No coupon for buy now (optional)
            discount_amount = 0
            final_price = total_price

            return render(request, 'checkout.html', {
                'cart_items': [{
                    'product': product,
                    'quantity': 1,
                }],
                'total_mrp': total_mrp,
                'total_price': total_price,
                'discount_amount': discount_amount,
                'final_price': final_price,
                'buy_now': True,
                'buy_now_id': product.id
            })

        # ================= CART =================
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('cart_list')

        total_mrp = 0
        total_price = 0

        for item in cart_items:
            mrp = item.product.discount if item.product.discount else item.product.price
            total_mrp += mrp * item.quantity
            total_price += item.product.price * item.quantity

        # ✅ APPLY COUPON
        coupon_id = None if buy_now_id else request.session.get('coupon_id')
        discount_amount = 0

        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                today = timezone.now().date()

                if coupon.valid_from <= today <= coupon.valid_to:

                    if coupon.discount_type == 'percent':
                        discount_amount = (total_price * coupon.discount_value) / 100
                    else:
                        discount_amount = coupon.discount_value

            except Coupon.DoesNotExist:
                pass

        # ✅ SAFETY
        if discount_amount > total_price:
            discount_amount = total_price

        final_price = total_price - discount_amount

        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'total_mrp': total_mrp,
            'total_price': total_price,
            'discount_amount': discount_amount,
            'final_price': final_price,
            'buy_now': False
        })


    def post(self, request):
        buy_now_id = request.POST.get('buy_now_id')

        address = request.POST.get('address') or request.user.address
        phone = request.POST.get('phone') or request.user.contact_number
        payment_method = request.POST.get('payment_method', 'COD')

        # ================= BUY NOW =================
        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)

            order = Order.objects.create(
                user=request.user,
                full_name=request.user.get_full_name(),
                address=address,
                phone=phone,
                payment_method=payment_method,
                total_price=product.price
            )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )

            return redirect('my_orders', order_id=order.id)

        # ================= CART =================
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty")
            return redirect('cart_list')

        # ✅ CALCULATE TOTAL
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # ✅ APPLY COUPON AGAIN (IMPORTANT)
        coupon_id = None if buy_now_id else request.session.get('coupon_id')
        discount_amount = 0

        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)

                if coupon.discount_type == 'percent':
                    discount_amount = (total_price * coupon.discount_value) / 100
                else:
                    discount_amount = coupon.discount_value

            except Coupon.DoesNotExist:
                pass

        if discount_amount > total_price:
            discount_amount = total_price

        final_price = total_price - discount_amount

        # ✅ CREATE ORDER WITH FINAL PRICE
        order = Order.objects.create(
            user=request.user,
            full_name=request.user.get_full_name(),
            address=address,
            phone=phone,
            payment_method=payment_method,
            total_price=final_price   # 🔥 IMPORTANT
        )

        # ✅ SAVE ITEMS
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # ✅ SAVE COUPON USAGE
        if coupon_id:
            from cart.models import CouponUsage
            coupon = Coupon.objects.get(id=coupon_id)

            CouponUsage.objects.create(
                user=request.user,
                coupon=coupon
            )

            del request.session['coupon_id']

        cart_items.delete()

        return redirect('order_detail', order_id=order.id)


class MyOrdersView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-id')
        return render(request, 'order.html', {'orders': orders}) 

class PaymentView(LoginRequiredMixin, View):
    template_name = 'payment.html'

    def get(self, request):
        buy_now_id = request.GET.get('buy_now')
        reorder_id = request.GET.get('reorder')

        coupon_id = None if buy_now_id else request.session.get('coupon_id')
        coupon_discount = 0
        coupon_code = ''

        # ================= REORDER =================
        if reorder_id:
            old_order = get_object_or_404(Order, id=reorder_id, user=request.user)

            total_price = sum(item.price * item.quantity for item in old_order.items.all())

        # ================= BUY NOW =================
        elif buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)
            total_price = product.price

        # ================= CART =================
        else:
            cart_items = Cart.objects.filter(user=request.user)
            total_price = sum(i.product.price * i.quantity for i in cart_items)

        # ================= APPLY COUPON AFTER TOTAL =================
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                coupon_code = coupon.code

                if coupon.discount_type == 'percent':
                    coupon_discount = (total_price * coupon.discount_value) / 100

                elif coupon.discount_type == 'flat':
                    coupon_discount = coupon.discount_value

            except Coupon.DoesNotExist:
                pass
        reward_coupon = request.session.pop("reward_coupon", None)
        # ✅ SAFETY
        if coupon_discount > total_price:
            coupon_discount = total_price

        final_price = total_price - coupon_discount

        # ================= RETURN =================
        context = {
            'total_price': total_price,
            'final_price': final_price,
            'coupon_discount': coupon_discount,
            'coupon_code': coupon_code,
            'items_count': 1 if buy_now_id else (
                old_order.items.count() if reorder_id else Cart.objects.filter(user=request.user).count()
            ),
            'buy_now': bool(buy_now_id),
            'reorder': bool(reorder_id),
            'reward_coupon' : reward_coupon
        }

        if buy_now_id:
            context['product'] = product
        if reorder_id:
            context['old_order'] = old_order

        return render(request, self.template_name, context)
    
    def post(self, request):
        buy_now_id = request.POST.get('buy_now_id')
        reorder_id = request.POST.get('reorder_id')
        payment_method = request.POST.get('payment_method', 'COD')

        coupon_id = request.session.get('coupon_id')
        coupon_discount = 0

        total_price = 0  # ✅ DEFINE FIRST

        # ================= REORDER =================
        if reorder_id:
            old_order = get_object_or_404(Order, id=reorder_id, user=request.user)

            for item in old_order.items.all():
                total_price += item.price * item.quantity

        # ================= BUY NOW =================
        elif buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)
            total_price = product.price

        # ================= CART =================
        else:
            cart_items = Cart.objects.filter(user=request.user)

            for item in cart_items:
                total_price += item.product.price * item.quantity

        # ================= APPLY COUPON =================
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)

                if coupon.discount_type == 'percent':
                    coupon_discount = (total_price * coupon.discount_value) / 100

                elif coupon.discount_type == 'flat':
                    coupon_discount = coupon.discount_value

            except Coupon.DoesNotExist:
                pass

        if coupon_discount > total_price:
            coupon_discount = total_price

        final_price = total_price - coupon_discount

        # ================= CREATE ORDER =================
        order = Order.objects.create(
            user=request.user,
            full_name=request.user.get_full_name(),
            address=request.user.address,
            phone=request.user.contact_number,
            payment_method=payment_method,
            total_price=final_price
        )

        # ================= ADD ITEMS =================
        if reorder_id:
            for item in old_order.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.price
                )

        elif buy_now_id:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )

        else:
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            cart_items.delete()

        # ================= PAYMENT =================
        if payment_method == "Online":
            order.is_paid = True
            order.save()

        generate_invoice(order)

        coupon_id = request.session.get('coupon_id')

        # ================= SAVE USED COUPON =================
        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)

                CouponUsage.objects.get_or_create(
                    user=request.user,
                    coupon=coupon
                )

            except Coupon.DoesNotExist:
                pass

            request.session.pop('coupon_id', None)

        return redirect('order_detail', order_id=order.id)

class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order,id=order_id,user=request.user)
        return render(request, 'order_detail.html', {'order': order})

class OrderStatusView(View):
    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return JsonResponse({'status': order.status})
    
class ReOrderView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        old_order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

        # ✅ CREATE NEW ORDER
        new_order = Order.objects.create(
            user=request.user,
            full_name=old_order.full_name,
            address=old_order.address,
            phone=old_order.phone,
            payment_method=old_order.payment_method,
            total_price=0,
            reordered_from=old_order,   
        )

        total_price = 0

        for item in old_order.items.all():
            OrderItem.objects.create(
                order=new_order,
                product=item.product,
                quantity=item.quantity,
                price=item.price
            )
            total_price += item.price * item.quantity

        new_order.total_price = total_price
        new_order.save()

        return redirect('order_detail', order_id=new_order.id)
    
class CancelOrderView(LoginRequiredMixin, View):
    def post(self, request, order_id):

        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status not in ["Pending", "Accepted"]:
            messages.error(request, "This order cannot be cancelled.")
            return redirect("order_detail", order_id=order.id)

        reason = request.POST.get("reason")

        # Update order status
        order.status = "Cancelled"
        order.save(update_fields=["status"])

        # Create or update cancellation record
        CancelledOrder.objects.update_or_create(
            order=order,
            defaults={"reason": reason}
        )

        messages.success(request, "Order cancelled successfully.")
        return redirect("order_detail", order_id=order.id)

class InvoiceDownloadView(LoginRequiredMixin, View):
    def get(self, request, order_id):

        invoice = get_object_or_404(Invoice, order_id=order_id)

        # Allow only order owner OR admin
        if request.user != invoice.order.user and not request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to access this invoice.")

        response = FileResponse(
            invoice.invoice_file.open('rb'),
            content_type='application/pdf'
        )

        response['Content-Disposition'] = f'inline; filename="{invoice.invoice_file.name}"'

        return response

class FeedbackCreateView(CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = "orders/feedback_form.html"

    def dispatch(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs["order_id"])
        if hasattr(order, "feedback"):
            return redirect("order_detail", order.id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        order = get_object_or_404(Order, id=self.kwargs["order_id"])

        # First product of order (simple case)
        product = order.items.first().product

        form.instance.order = order
        form.instance.product = product

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "order_detail",
            kwargs={"order_id": self.kwargs["order_id"]}
        )