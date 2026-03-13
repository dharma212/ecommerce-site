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
from .utils import generate_invoice
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

        payment_method = request.POST.get('payment_method', 'COD')
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
                payment_method=payment_method,
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
            
            if payment_method == "Online":
                new_order.is_paid = True
                
            new_order.save()
            generate_invoice(new_order)


            return redirect('order_detail', order_id=new_order.id)

        # ================= BUY NOW =================
        order = Order.objects.create(
            user=request.user,
            full_name=request.user.get_full_name(),
            address=request.user.address,
            phone=request.user.contact_number,
            payment_method=payment_method,
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
        
        if payment_method == "Online":
            order.is_paid = True
        
        order.save()
        generate_invoice(order)

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

# from django.views import View
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
# from django.contrib.auth.mixins import LoginRequiredMixin
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.units import inch
# from datetime import date
# from decimal import Decimal

# class InvoiceDownloadView(LoginRequiredMixin, View):
#     def get(self, request, order_id, *args, **kwargs):
#         order = get_object_or_404(Order, id=order_id, user=request.user)

#         response = HttpResponse(content_type="application/pdf")
#         filename = f"Tax-Invoice-{order.id}.pdf"
#         response["Content-Disposition"] = f'attachment; filename="{filename}"'

#         doc = SimpleDocTemplate(
#             response,
#             pagesize=(8.5*inch, 11*inch),
#             rightMargin=40,
#             leftMargin=40,
#             topMargin=40,
#             bottomMargin=40
#         )

#         styles = getSampleStyleSheet()
#         # Custom Style for clean headers
#         styles['Normal'].fontSize = 9
#         styles['Normal'].leading = 12
        
#         elements = []

#         # ================= HEADER / BRANDING =================
#         header_data = [
#             [Paragraph("<b>E COMMERCE PVT LTD</b>", styles["Title"]), 
#              Paragraph("<b>TAX INVOICE</b>", styles["Heading2"])]
#         ]
#         header_tab = Table(header_data, colWidths=[4*inch, 3.5*inch])
#         header_tab.setStyle(TableStyle([
#             ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
#             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#         ]))
#         elements.append(header_tab)
#         elements.append(Spacer(1, 20))

#         # ================= INVOICE DETAILS =================
#         # Two columns: Seller info and Invoice meta-data
#         meta_data = [
#             [
#                 Paragraph("<b>FROM:</b><br/>E Commerce Pvt Ltd<br/>GSTIN: 24ABCDE1234F1Z5<br/>Ahmedabad, Gujarat - 380001", styles["Normal"]),
#                 Paragraph(f"<b>Invoice No:</b> INV-{order.id}<br/><b>Date:</b> {date.today()}<br/><b>Order ID:</b> {order.id}", styles["Normal"])
#             ]
#         ]
#         meta_tab = Table(meta_data, colWidths=[3.75*inch, 3.75*inch])
#         elements.append(meta_tab)
#         elements.append(Spacer(1, 15))

#         # ================= BILLING DETAILS =================
#         bill_to = [
#             [Paragraph(f"<b>BILL TO:</b><br/>{order.user.get_full_name()}<br/>{order.address}<br/>Phone: {order.phone}", styles["Normal"])]
#         ]
#         bill_tab = Table(bill_to, colWidths=[7.5*inch])
#         bill_tab.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
#             ('TOPPADDING', (0, 0), (-1, -1), 10),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
#             ('LEFTPADDING', (0, 0), (-1, -1), 10),
#         ]))
#         elements.append(bill_tab)
#         elements.append(Spacer(1, 25))

#         # ================= PRODUCT TABLE =================
#         product_data = [["Description", "Qty", "Price", "CGST", "SGST", "Total"]]

#         taxable_value = Decimal("0.00")
#         cgst_total = Decimal("0.00")
#         sgst_total = Decimal("0.00")
#         total_amount = Decimal("0.00")

#         for item in order.items.all():
#             amount = item.price * item.quantity
#             base_price = amount / Decimal("1.18")
#             cgst = base_price * Decimal("0.09")
#             sgst = base_price * Decimal("0.09")

#             taxable_value += base_price
#             cgst_total += cgst
#             sgst_total += sgst
#             total_amount += amount

#             product_data.append([
#                 Paragraph(item.product.name, styles["Normal"]),
#                 item.quantity,
#                 f"{base_price:.2f}",
#                 f"{cgst:.2f}",
#                 f"{sgst:.2f}",
#                 f"{amount:.2f}",
#             ])

#         # Modern Table Style (Clean lines, no side borders)
#         product_table = Table(product_data, colWidths=[3*inch, 0.6*inch, 1*inch, 0.8*inch, 0.8*inch, 1.3*inch])
#         product_table.setStyle(TableStyle([
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, 0), 10),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#333333")),
#             ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
#             ('ALIGN', (0, 0), (0, -1), 'LEFT'),
#             ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'), # Total column right-aligned
#             ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
#             ('LINEBELOW', (0, 1), (-1, -2), 0.5, colors.grey), # Thin lines between items
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('TOPPADDING', (0, 0), (-1, -1), 8),
#             ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
#         ]))
#         elements.append(product_table)

#         # ================= TOTALS SECTION =================
#         payment_charge = Decimal("47.00") if order.payment_method == "cod" else Decimal("7.00")
#         grand_total = total_amount + payment_charge

#         totals_data = [
#             ["", "Taxable Value:", f"Rs. {taxable_value:.2f}"],
#             ["", "CGST (9%):", f"Rs. {cgst_total:.2f}"],
#             ["", "SGST (9%):", f"Rs. {sgst_total:.2f}"],
#             ["", "Shipping/Charges:", f"Rs. {payment_charge:.2f}"],
#             ["", "Grand Total:", f"Rs. {grand_total:.2f}"],
#         ]
        
#         totals_tab = Table(totals_data, colWidths=[4*inch, 2*inch, 1.5*inch])
#         totals_tab.setStyle(TableStyle([
#             ('ALIGN', (1, 0), (1, -1), 'LEFT'),
#             ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
#             ('FONTNAME', (1, -1), (2, -1), 'Helvetica-Bold'),
#             ('TOPPADDING', (0, 0), (-1, -1), 3),
#             ('LINEABOVE', (1, -1), (2, -1), 1, colors.black), # Line above Grand Total
#         ]))
#         elements.append(Spacer(1, 10))
#         elements.append(totals_tab)

#         # ================= FOOTER =================
#         elements.append(Spacer(1, 40))
#         elements.append(Paragraph("<b>Notes & Declaration:</b>", styles["Normal"]))
#         elements.append(Paragraph("1. All disputes are subject to Ahmedabad jurisdiction.", styles["Normal"]))
#         elements.append(Paragraph("2. This is a computer-generated invoice and does not require a physical signature.", styles["Normal"]))

#         doc.build(elements)
#         return response
    
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

from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from order.models import Invoice

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

# views.py
from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Feedback, Order
from .forms import FeedbackForm

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