from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CategoryForm, ProductForm, ProductImageForm
from .models import ProductImage
from django.views.generic import ListView
from .models import *
from django.views.generic import ListView, FormView, UpdateView, DeleteView,CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from product.models import Category, SubCategory
from product.forms import CategoryForm, SubCategoryForm
from django.contrib.auth.mixins import LoginRequiredMixin

# -----------------------
# Category Views
# -----------------------
class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "category_form.html"
    success_url = reverse_lazy("product:categoery_list")

    def form_valid(self, form):
        messages.success(self.request, "Category created successfully!")
        return super().form_valid(form)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "dashboard/category_list.html"
    context_object_name = "categories"

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "dashboard/category_edit.html"
    success_url = reverse_lazy("dashboard:categoery_list")

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully!")
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy("dashboard:categoery_list")

    def post(self, request, *args, **kwargs):
        messages.success(request, "Category deleted successfully!")
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

# -----------------------
# SubCategory Views
# -----------------------
class SubCategoryCreateView(LoginRequiredMixin, FormView):
    model = SubCategory
    template_name = "dashboard/subcategory_form.html"
    form_class = SubCategoryForm
    success_url = reverse_lazy("product:subcategory_list")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "SubCategory created successfully!")
        return super().form_valid(form)

class SubCategoryListView(LoginRequiredMixin, ListView):
    model = SubCategory
    template_name = "dashboard/subcategory_list.html"
    context_object_name = "subcategories"

class SubCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = SubCategory
    form_class = SubCategoryForm
    template_name = "dashboard/sub_category_edit.html"
    success_url = reverse_lazy("product:subcategory_list")

    def form_valid(self, form):
        messages.success(self.request, "Sub Category updated successfully!")
        return super().form_valid(form)

class SubCategoryDeleteView(DeleteView):
    model = SubCategory
    success_url = reverse_lazy("product:subcategory_list")

    def post(self, request, *args, **kwargs):
        messages.success(request, "Sub Category deleted successfully!")
        return super().post(request, *args, **kwargs)


# =============================
# ===== Create Product ========
# =============================
class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm # Ensure ProductForm does NOT mention 'category'
    template_name = 'product_form.html'
    success_url = reverse_lazy('product:product_list')


    def form_valid(self, form):
        # Just save normally. 
        # Django will only look for the fields present in your models.py
        return super().form_valid(form)



# =============================
# === Add Product Image =======
# =============================

class ProductImageCreateView(FormView):
    template_name = "product_image_form.html"
    form_class = ProductImageForm
    success_url = reverse_lazy("product:add_product_image")

    def form_valid(self, form):
        product = form.cleaned_data["product"]
        name = form.cleaned_data.get("name", "")

        images = self.request.FILES.getlist("photos")

        if not images:
            messages.error(self.request, "Please select at least one image")
            return self.form_invalid(form)

        for image in images:
            ProductImage.objects.create(
                product=product,
                name=name,
                photo=image
            )

        messages.success(self.request, "Product images added successfully!")
        return super().form_valid(form)

class ProductListView(ListView):
    model = Product
    template_name = "dashboard/product_list.html"  # create this template
    context_object_name = "products"
