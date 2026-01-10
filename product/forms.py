from django import forms
from .models import Category, Product, ProductImage,Banner


# =======================
# CATEGORY FORM
# =======================
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "image", "description"]
        error_messages = {
            "name": {
                "required": "Category name is required."
            },
            "image": {
                "required": "Category image is required."
            },
            "description": {
                "required": "Category description is required."
            },
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter category name"
            }),
            "image": forms.ClearableFileInput(attrs={
            "class": "form-control",
            "accept": "image/*"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter category description",
                "rows": 3
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError("This Category Is Already Exists.")
        return name
    
# =======================
# PRODUCT FORM
# =======================
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "price", "discount","screen_size", "ram", "rom", "memory"]
        error_messages = {
            "name": {
                "required": "Product name is required."
            },
            "category": {
                "required": "Category is required."
            },
            "price": {
                "required": "Price is required.",
                "invalid": "Enter a valid price."
            },
            "discount": {
                "invalid": "Enter a valid discount."
            },
            "screen_size": {
                "required": "Screen size is required."
            },
            "ram": {
                "required": "RAM is required."
            },
            "rom": {
                "required": "ROM is required."
            },
            "memory": {
                "required": "Memory is required."
            },
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter product name"
            }),
            "category": forms.Select(attrs={
                "class": "form-control"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter price"
            }),
            "discount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter discount (%)"
            }),
            "screen_size": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Screen size (e.g. 6.5 inch)"
            }),
            "ram": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "RAM (e.g. 8GB)"
            }),
            "rom": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "ROM (e.g. 128GB)"
            }),
            "memory": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Memory (e.g. 1TB)"
            }),
        }
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Product.objects.filter(name=name).exists():
            raise forms.ValidationError("This Product Is Already Exists.")
        return name 
        
# =======================
# PRODUCT IMAGE FORM
# =======================
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["product", "name"]  # ✅ MATCH MODEL
        error_messages = {
            "product": {
                "required": "Product is required."
            },
            "name": {
                "required": "Image name is required."
            },
            "photo": {
                "required": "Image file is required."
            },
        }
        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Image name"
            }),
            "photo": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }
class BannerForm(forms.ModelForm):
    class Meta:
        model=Banner
        fields = ["title", "image","is_active"]

        error_messages = {
                "title": {
                    "required": "Banner Title is required."
                },
                "image": {
                    "required": "Banner image is required."
                },
                "is_active":{
                    "required":"checck the banner active mode"
                },
            
            }
        widgets = {
                "title": forms.TextInput(attrs={
                    "class": "form-control",
                    "placeholder": "Enter Bannner title"
                }),
                "image": forms.ClearableFileInput(attrs={
                    "class": "form-control",
                    "accept": "image/*"
                }),
                    "is_active": forms.CheckboxInput(attrs={
                    "class": "form-check-input",
                }),            
            }

    def clean_title(self):
        t = self.cleaned_data.get("title")
        if not t:
            return t
        if Banner.objects.filter(title__iexact=t).exists():
            raise forms.ValidationError("This banner title already exists.")
        return t
