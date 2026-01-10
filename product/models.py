from django.db import models
from users.models import BaseModel
# =====================
# Category Model
# =====================
class Banner(BaseModel):
    image=models.ImageField(upload_to="banner/",null=True,blank=True)
    title=models.CharField(max_length=50,unique=True)
    is_active=models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
class Category(BaseModel):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="categories/", blank=True,null=True)
    description = models.TextField()

    def __str__(self):
        return self.name

# =====================
# Product Model
# =====================
class Product(BaseModel):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="products")
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)
    screen_size = models.CharField(max_length=50)
    ram = models.CharField(max_length=50)
    rom = models.CharField(max_length=50)
    memory = models.CharField(max_length=50)


    def __str__(self):
        return self.name    


# =====================
# Product Image Model
# =====================
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="products/")  # ← NOT image

    def __str__(self):
        return self.product.name