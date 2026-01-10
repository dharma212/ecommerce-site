from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from .forms import CategoryForm, ProductForm, ProductImageForm
from .models import ProductImage
from django.views.generic import ListView
from .models import *
# =============================
# ===== Create Category =======
# =============================

class CategoryCreateView(FormView):
    template_name = "category_form.html"
    form_class = CategoryForm
    success_url = reverse_lazy("product:category_form")

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)  # important for images
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()  # image will be saved to 'media/categories/'
        messages.success(self.request, "Category created successfully!")
        return super().form_valid(form)

# =============================
# ===== Create Product ========
# =============================
class ProductCreateView(FormView):
    template_name = "product_form.html"
    form_class = ProductForm
    success_url = reverse_lazy("product:add_product")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Product created successfully!")
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
