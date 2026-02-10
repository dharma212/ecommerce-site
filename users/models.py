from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.conf import settings
from django.contrib.auth.models import AbstractUser


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(BaseModel, AbstractUser):
    ROLE_CHOICES = (('admin', 'Admin'),('customer', 'Customer'),)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='customer')
    contact_number = models.CharField(max_length=15,blank=True,null=True,unique=True)
    address = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
from django.db import models

class AboutPage(models.Model):
    store_name = models.CharField(max_length=100, default="Animataed", help_text="This will be the floating animated text.")
    hero_subtitle = models.CharField(max_length=255, help_text="Short catchy line under the title.")
    mission_statement = models.TextField(help_text="Your brand's 'Why'.")
    story_description = models.TextField(help_text="The full history of your store.")
    story_image = models.ImageField(upload_to='about_us/', blank=True, null=True)
    
    # Values Section
    value_one_title = models.CharField(max_length=100, default="Quality")
    value_one_desc = models.TextField()
    value_two_title = models.CharField(max_length=100, default="Innovation")
    value_two_desc = models.TextField()
    value_three_title = models.CharField(max_length=100, default="Community")
    value_three_desc = models.TextField(null=True)

    # class Meta:
    #     verbose_name_plural = "About Page Content"

    def __str__(self):
        return f"{self.store_name} Content Configuration"
    
from django.db import models

class TermsAndConditions(models.Model):
    title = models.CharField(max_length=200, default="Terms & Conditions")
    last_updated = models.DateField(auto_now=True)
    introduction = models.TextField()
    use_of_website = models.TextField()
    user_accounts = models.TextField()
    product_info = models.TextField()
    liability = models.TextField()
    changes_to_terms = models.TextField()

    class Meta:
        verbose_name_plural = "Terms & Conditions"

    def __str__(self):
        return f"{self.title} - {self.last_updated}"