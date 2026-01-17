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

from django.db import models
from users.models import BaseModel

# =====================
# Main Category
# =====================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# =====================
# SubCategory
# =====================
class SubCategory(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="subcategories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


# =====================
# Product Model
# =====================
class Product(models.Model):
    sub_category = models.ForeignKey(SubCategory,on_delete=models.CASCADE,related_name="products",null=True,blank=True)
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField()
    screen_size = models.CharField(max_length=50)
    ram = models.CharField(max_length=50)
    rom = models.CharField(max_length=50)
    memory = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)

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