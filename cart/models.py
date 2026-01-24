from django.db import models
from django.conf import settings
from product.models import Product
from users.models import BaseModel
class Cart(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    prise=models.FloatField(blank=True,null=True ,default=0.0)
    def __str__(self):
        return f"{self.user} - {self.product.name}"
