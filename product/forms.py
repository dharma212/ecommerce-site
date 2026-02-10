from django import forms
from .models import Category, Product, ProductImage,Banner,SubCategory
from django import forms

# -----------------------
# Category Form
# -----------------------
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# -----------------------
# SubCategory Form
# -----------------------
class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SubCategory Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }




# =======================
# PRODUCT FORM
# =======================
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sub_category",
            "price",
            "discount",
            "stock",
            "screen_size",
            "ram",
            "rom",
            "refresh_rate",
            "memory",
        ]
        widgets = {
    "name": forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter product name (e.g. Dell Inspiron 15)"
    }),
    "sub_category": forms.Select(attrs={
        "class": "form-control"
    }),
    "price": forms.NumberInput(attrs={
        "class": "form-control",
        "placeholder": "Enter price (e.g. 100000)"
    }),
    "discount": forms.NumberInput(attrs={
        "class": "form-control",
        "placeholder": "Enter discount amount or %"
    }),
    "stock": forms.NumberInput(attrs={
        "class": "form-control",
        "placeholder": "Enter available stock"
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
        "placeholder": "Storage / ROM (e.g. 128GB)"
    }),
    "refresh_rate": forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Refresh Rate (e.g. 60Hz / 120Hz)"
    }),
    "memory": forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Expandable memory (e.g. 1TB)"
    }),
}


    # def clean_name(self):
    #     name = self.cleaned_data.get("name")
    #     if Product.objects.filter(name=name).exists():
    #         raise forms.ValidationError("This Product already exists.")
    #     return name

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