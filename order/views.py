from django.views import View
from cart.models import Cart
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from product.models import Product
from .models import Order, OrderItem, CancelledOrder
from django.http import HttpResponse
from datetime import date
from openpyxl import Workbook

class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):
        buy_now_id = request.GET.get('buy_now')

        # ✅ BUY NOW FLOW
        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)

            return render(request, 'checkout.html', {
                'cart_items': [{
                    'product': product,
                    'quantity': 1,
                }],
                'total_price': product.price,
                'buy_now': True,
                'buy_now_id': product.id
            })

        # ✅ CART FLOW
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('cart_list')

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
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

        order = Order.objects.create(
            user=request.user,
            full_name=request.user.get_full_name(),
            address=address,
            phone=phone,
            payment_method=payment_method,
            total_price=0
        )

        total_price = 0
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            total_price += item.product.price * item.quantity

        order.total_price = total_price
        order.save()

        cart_items.delete()

        return redirect('order_detail', order_id=order.id)


class MyOrdersView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-id')
        print(orders)
        return render(request, 'order.html', {'orders': orders}) 

class PaymentView(LoginRequiredMixin, View):
    template_name = 'payment.html'

    def get(self, request):
        buy_now_id = request.GET.get('buy_now')
        reorder_id = request.GET.get('reorder')

        # ✅ RE-ORDER FLOW
        if reorder_id:
            old_order = get_object_or_404(
                Order,
                id=reorder_id,
                user=request.user
            )

            total_price = sum(
                item.price * item.quantity
                for item in old_order.items.all()
            )

            return render(request, self.template_name, {
                'total_price': total_price,
                'items_count': old_order.items.count(),
                'reorder': True,
                'old_order': old_order
            })


        # ✅ BUY NOW FLOW
        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)

            total_price = product.price
            items_count = 1

            return render(request, self.template_name, {
                'total_price': total_price,
                'items_count': items_count,
                'buy_now': True,
                'product': product
            })

        # ✅ CART FLOW
        cart_items = Cart.objects.filter(user=request.user)

        total_price = sum(i.product.price * i.quantity for i in cart_items)

        return render(request, self.template_name, {
            'total_price': total_price,
            'items_count': cart_items.count(),
            'buy_now': False
        })
    
    def post(self, request):
        buy_now_id = request.POST.get('buy_now_id')
        reorder_id = request.POST.get('reorder_id')

        # ================= RE-ORDER =================
        if reorder_id:
            old_order = get_object_or_404(
                Order,
                id=reorder_id,
                user=request.user
            )

            # ✅ CREATE NEW ORDER
            new_order = Order.objects.create(
                user=request.user,
                full_name=request.user.get_full_name(),
                address=old_order.address,
                phone=old_order.phone,
                payment_method='COD',
                total_price=0
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
            new_order.reordered_from = old_order
            new_order.save()
            

            return redirect('order_detail', order_id=new_order.id)

        # ================= BUY NOW =================
        order = Order.objects.create(
            user=request.user,
            full_name=request.user.get_full_name(),
            address=request.user.address,
            phone=request.user.contact_number,
            payment_method='COD',
            total_price=0
        )

        total_price = 0

        if buy_now_id:
            product = get_object_or_404(Product, id=buy_now_id)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )
            total_price = product.price

        # ================= CART =================
        else:
            cart_items = Cart.objects.filter(user=request.user)

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                total_price += item.product.price * item.quantity

            cart_items.delete()

        order.total_price = total_price
        order.save()

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
            reordered_from=old_order,   # ⭐ THIS IS THE KEY
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

class InvoiceDownloadView(LoginRequiredMixin, View):
    def get(self, request, order_id, *args, **kwargs):

        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

        wb = Workbook()
        ws = wb.active
        ws.title = "Invoice"

        # ===== ORDER INFO =====
        ws.append(["Invoice"])
        ws.append([])
        ws.append(["Order ID", order.id])
        ws.append(["Customer Name", order.user.get_full_name()])
        ws.append(["Phone", order.phone])
        ws.append(["Address", order.address])
        ws.append(["Payment Method", order.get_payment_method_display()])
        ws.append(["Order Date", order.created_at.strftime("%Y-%m-%d")])
        ws.append([])

        # ===== TABLE HEADER =====
        ws.append([
            "Product",
            "Quantity",
            "Price",
            "Total"
        ])

        # ===== ITEMS =====
        for item in order.items.all():
            ws.append([
                item.product.name,
                item.quantity,
                float(item.price),
                float(item.price * item.quantity),
            ])

        ws.append([])
        ws.append(["Total Amount", "", "", float(order.total_price)])

        # ===== FILE RESPONSE =====
        today = date.today().strftime("%Y-%m-%d")
        filename = f"invoice-order-{order.id}-{today}.xlsx"

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        wb.save(response)
        return response

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

        