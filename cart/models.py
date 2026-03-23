from django.db import models
from django.conf import settings
from product.models import Product
from users.models import BaseModel

class Cart(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user} - {self.product.name}"


class Wishlist(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} - {self.product.name}"

class Coupon(models.Model):

    DISCOUNT_TYPE = (
        ('percent', 'Percentage'),
        ('flat', 'Flat'),
    )

    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE, default='percent')
    discount_value = models.IntegerField()

    min_amount = models.IntegerField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
    
# from django.contrib.auth.models import User
from users.models import User
class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'coupon')  # 🔥 prevent duplicate use

    def __str__(self):
        return f"{self.user} used {self.coupon.code}"
    
