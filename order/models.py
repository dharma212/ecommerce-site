from django.db import models
from django.conf import settings
from product.models import Product
from users.models import BaseModel  

class Order(BaseModel):
    PAYMENT_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('Online', 'Online Payment'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)
    full_name = models.CharField(max_length=100, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2) 
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='COD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_paid = models.BooleanField(default=False)
    reordered_from = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reorders'
    )
    
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"
    
    @property
    def is_reorder(self):
        return self.reordered_from is not None



class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order: {self.order.id})"
    
class CancelledOrder(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='cancellation')
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cancelled Order {self.order.id}"