from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from product.models import Product
from cart.models import *
from django.http import JsonResponse
from django.views.generic import ListView
from django.db.models import Sum, F
# from .models import CartItem


from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, F
from cart.models import Cart

class CartCountView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"count": 0, "total": 0})

        cart_items = Cart.objects.filter(user=request.user)

        count = cart_items.aggregate(
            total_qty=Sum("quantity")
        )["total_qty"] or 0

        total_amount = cart_items.aggregate(
            total=Sum(F("quantity") * F("product__price"))
        )["total"] or 0

        return JsonResponse({
            "count": count,
            "total": float(total_amount)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_price = sum(item.product.price * item.quantity for item in context['cart_items'] if item.product.stock > 0)
        context['total_price'] = total_price
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

# ================= TOGGLE WISHLIST =================
class ToggleWishlistView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        if not product_id:
            return JsonResponse({"status": "error", "message": "No product id provided"})
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Product not found"})
        
        wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
        if wishlist_item:
            wishlist_item.delete()
            return JsonResponse({"status": "removed", "product_id": product.id})
        else:
            Wishlist.objects.create(user=request.user, product=product)
            return JsonResponse({"status": "added", "product_id": product.id})

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

        if action == "plus":
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
            else:
                return JsonResponse({"success": False, "error": f"Only {product.stock} items in stock!"})
        elif action == "minus":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
        
        cart_item.save()

        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(i.product.price * i.quantity for i in cart_items)

        return JsonResponse({
            "success": True,
            "quantity": cart_item.quantity,
            "total_price": total_price
        })
        
        