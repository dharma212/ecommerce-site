from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from product.models import Product
from cart.models import *
from django.http import JsonResponse
from django.views.generic import ListView
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, F
from django.utils import timezone
from .models import Coupon
from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import Coupon, Cart

class CartCountView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"count": 0, "total": 0})

        cart_items = Cart.objects.filter(user=request.user)

        # ✅ Count
        count = cart_items.aggregate(
            total_qty=Sum("quantity")
        )["total_qty"] or 0

        # ✅ Total price
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        # ✅ Apply coupon
        coupon_id = request.session.get('coupon_id')
        discount_amount = 0

        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                today = timezone.now().date()

                if coupon.valid_from <= today <= coupon.valid_to:

                    if coupon.discount_type == 'percent':
                        discount_amount = (total_amount * coupon.discount_value) / 100

                    elif coupon.discount_type == 'flat':
                        discount_amount = coupon.discount_value

            except Coupon.DoesNotExist:
                pass

        # ✅ Safety
        if discount_amount > total_amount:
            discount_amount = total_amount

        final_total = total_amount - discount_amount

        return JsonResponse({
            "count": count,
            "total": float(final_total)
        })

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


class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'cart_list.html'
    context_object_name = 'cart_items'

    # ✅ Get cart items + stock fix
    def get_queryset(self):
        items = Cart.objects.select_related('product').filter(user=self.request.user)

        for item in items:
            if item.product.stock > 0 and item.quantity > item.product.stock:
                item.quantity = item.product.stock
                item.save()
            elif item.product.stock == 0:
                item.quantity = 0
                item.save()

        return items

    # ✅ Main logic
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = context['cart_items']

        # ==============================
        # ✅ Step 1: Calculate totals
        # ==============================
        total_selling_price = 0
        total_mrp = 0

        for item in cart_items:
            if item.product.stock > 0:

                # Selling price
                item_selling_total = item.product.price * item.quantity

                # MRP (original price)
                mrp = item.product.discount if item.product.discount else item.product.price
                item_mrp_total = mrp * item.quantity

                total_selling_price += item_selling_total
                total_mrp += item_mrp_total


        # ==============================
        # ✅ Step 2: Apply Coupon
        # ==============================
        coupon_discount_amount = 0
        coupon_id = self.request.session.get('coupon_id')

        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)
                today = timezone.now().date()

                # ✅ Check validity + minimum amount
                if (
                    coupon.valid_from <= today <= coupon.valid_to and
                    total_selling_price >= coupon.min_amount
                ):

                    # 🔥 Handle BOTH types
                    if coupon.discount_type == 'percent':
                        coupon_discount_amount = (total_selling_price * coupon.discount_value) / 100

                    elif coupon.discount_type == 'flat':
                        coupon_discount_amount = coupon.discount_value

                else:
                    # ❌ Remove invalid coupon
                    self.request.session['coupon_id'] = None

            except Coupon.DoesNotExist:
                pass


        # ==============================
        # ✅ Step 3: Safety check
        # ==============================
        if coupon_discount_amount > total_selling_price:
            coupon_discount_amount = total_selling_price


        # ==============================
        # ✅ Step 4: Final calculations
        # ==============================
        final_price = total_selling_price - coupon_discount_amount

        product_savings = total_mrp - total_selling_price
        total_savings = product_savings + coupon_discount_amount


        # ==============================
        # ✅ Step 5: Send to template
        # ==============================
        context.update({
            'total_price': total_selling_price,
            'total_mrp': total_mrp,
            'discount_amount': coupon_discount_amount,
            'final_price': final_price,
            'total_savings': total_savings,
        })

        return context

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
    
class RemoveFromCartAjaxView(LoginRequiredMixin, View):
    def post(self, request):
        item_id = request.POST.get("item_id")
        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        cart_item.delete()

        # updated cart info
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(i.product.price * i.quantity for i in cart_items)

        return JsonResponse({
            "success": True,
            "cart_count": cart_items.count(),
            "total_price": total_price
        })

class WishlistListView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'wishlist_list.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        return (
            Wishlist.objects
            .select_related('product')
            .filter(user=self.request.user)
            .order_by('-created_at')  # latest first
        )

class WishlistToggleAjaxView(LoginRequiredMixin, View):
    login_url = "/user/login/"

    def post(self, request):
        product_id = request.POST.get("product_id")
        product = Product.objects.get(id=product_id)

        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            product=product
        )

        if wishlist_item.exists():
            wishlist_item.delete()
            return JsonResponse({"status": "removed"})
        else:
            Wishlist.objects.create(
                user=request.user,
                product=product
            )
            return JsonResponse({"status": "added"})
        
class RemoveFromWishlistAjaxView(LoginRequiredMixin, View):
    def post(self, request):
        item_id = request.POST.get("item_id")

        wishlist_item = get_object_or_404(
            Wishlist, id=item_id, user=request.user
        )
        wishlist_item.delete()

        wishlist_items = Wishlist.objects.filter(user=request.user)

        return JsonResponse({
            "success": True,
            "wishlist_count": wishlist_items.count()
        })

class MoveWishlistToCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get("item_id")

        if not item_id:
            return JsonResponse({"success": False, "error": "No item id"})

        try:
            wishlist_item = Wishlist.objects.get(
                id=item_id,
                user=request.user
            )

            product = wishlist_item.product

            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={"quantity": 1}
            )

            if not created:
                cart_item.quantity += 1
                cart_item.save()

            wishlist_item.delete()

            return JsonResponse({"success": True})

        except Wishlist.DoesNotExist:
            return JsonResponse({"success": False, "error": "Wishlist item not found"})

# ================= ADD TO CART  =================
class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        
        if not created:
            if cart_item.quantity >= product.stock:
                return JsonResponse({"success": False, "error": "Out of stock!"})
            cart_item.quantity += 1
            cart_item.save()
        else:
            if product.stock < 1:
                cart_item.delete()
                return JsonResponse({"success": False, "error": "Product is out of stock!"})
        
        return JsonResponse({"success": True, "product_id": product.id})

# ================= GET CURRENT CART & WISHLIST =================
class GetCartWishlistView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user).values_list('product_id', flat=True)
        wishlist_items = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        return JsonResponse({
            "cart": list(cart_items),
            "wishlist": list(wishlist_items)
        })


# ================= UPDATE QUANTITY (With Stock Check) =================
class UpdateCartQtyAjaxView(LoginRequiredMixin, View):
    def post(self, request):
        item_id = request.POST.get("item_id")
        action = request.POST.get("action")

        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        product = cart_item.product

        # ✅ Update quantity
        if action == "plus":
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
            else:
                return JsonResponse({
                    "success": False,
                    "error": f"Only {product.stock} items in stock!"
                })

        elif action == "minus":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1

        cart_item.save()

        # ✅ Calculate total price FIRST
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(i.product.price * i.quantity for i in cart_items)

        # ✅ Apply coupon
        coupon_id = request.session.get('coupon_id')
        discount_amount = 0

        if coupon_id:
            try:
                coupon = Coupon.objects.get(id=coupon_id)

                if coupon.discount_type == 'percent':
                    discount_amount = (total_price * coupon.discount_value) / 100
                elif coupon.discount_type == 'flat':
                    discount_amount = coupon.discount_value

            except Coupon.DoesNotExist:
                pass

        # ✅ Safety check
        if discount_amount > total_price:
            discount_amount = total_price

        final_price = total_price - discount_amount

        return JsonResponse({
            "success": True,
            "quantity": cart_item.quantity,
            "total_price": final_price,
            "discount": discount_amount
        })

class ApplyCouponView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "Please login first ❌")
            return redirect('login')

        code = request.POST.get('coupon_code')
        request.session.pop('coupon_id', None)

        today = timezone.now().date()

        coupon = Coupon.objects.filter(
            code__iexact=code,
            active=True,
            valid_from__lte=today,
            valid_to__gte=today
        ).order_by('-id').first()   

        if not coupon:
            messages.error(request, "Invalid or expired coupon ")
            return redirect('cart_list')

        # ✅ CHECK ALREADY USED
        if CouponUsage.objects.filter(user=request.user, coupon=coupon).exists():
            messages.error(request, "Coupon already used ")
            return redirect('cart_list')

        # ✅ CART TOTAL
        cart_items = Cart.objects.filter(user=request.user)
        total = sum(item.product.price * item.quantity for item in cart_items)

        # ❌ MINIMUM AMOUNT
        if total < coupon.min_amount:
            messages.error(request, f"Minimum order ₹{coupon.min_amount} required")
            return redirect('cart_list')

        # ✅ APPLY
        request.session['coupon_id'] = coupon.id
        messages.success(request, "Coupon applied successfully ")

        return redirect('cart_list')
    
class CouponListView(LoginRequiredMixin, ListView):
    model = Coupon
    template_name = "coupon.html"
    context_object_name = "coupons"

    def get_queryset(self):
        return Coupon.objects.all().order_by('-valid_to')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        used_coupons = CouponUsage.objects.filter(
            user=self.request.user
        ).values_list('coupon_id', flat=True)

        context['used_coupons'] = used_coupons
        return context
    
from django.views import View
from django.http import JsonResponse

class ClearCouponPopupView(View):
    def post(self, request):
        request.session.pop('show_coupon_popup', None)
        request.session.pop('popup_coupon_id', None)

        return JsonResponse({"success": True})