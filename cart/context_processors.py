from .models import Cart
from django.db import models

def cart_count(request):
    if request.user.is_authenticated:
        # Sum of all quantities in the cart
        count = Cart.objects.filter(user=request.user).aggregate(
            total=models.Sum("quantity")
        )["total"] or 0
        return {"cart_count": count}
    return {"cart_count": 0}