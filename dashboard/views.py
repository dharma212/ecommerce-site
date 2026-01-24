# ===========================
# Django Core Imports
# ===========================
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (TemplateView,FormView,ListView,CreateView,DeleteView,UpdateView)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from users.forms import UserProfileUpdateForm
from django.contrib.auth.views import LoginView


# ===========================
# Models Imports
# ===========================
from users.models import *
from product.models import *

# ===========================
# Forms Imports
# ===========================
from product.forms import *
from .forms import UserForm
from django.core.exceptions import PermissionDenied
from django.core.exceptions import PermissionDenied

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render

class DashboardLoginRequiredMixin(LoginRequiredMixin):
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # show a custom page instead of redirect
            return render(request, 'index.html')
        return super().dispatch(request, *args, **kwargs)


# ===========================
# Dashboard Index
# ===========================
class DashbboardIndexView(DashboardLoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"


# ===========================
# Users Section
# ===========================
User = get_user_model()

class AllUserView(DashboardLoginRequiredMixin,TemplateView):
    template_name = "dashboard/all-user.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_user"] = User.objects.all()
        return context

class UserListView(DashboardLoginRequiredMixin,LoginRequiredMixin, ListView):
    model = User
    template_name = "dashboard/all-user.html"
    context_object_name = "all_user"

class UserCreateView(DashboardLoginRequiredMixin,LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "dashboard/add_user.html"
    success_url = reverse_lazy("user_list")
    success_message = "User added successfully"

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()
        return super().form_valid(form)

User = get_user_model()

class UserDeleteView(DashboardLoginRequiredMixin,SuccessMessageMixin, DeleteView):
    model = User
    success_url = reverse_lazy("user_list")
    # success_message = "User deleted successfully"

    def post(self, request, *args, **kwargs):
        user_to_delete = self.get_object()

        if user_to_delete == request.user:
            messages.error(request, "You cannot delete your own account.")
            return redirect("user_list")

        messages.success(request, "User deleted successfully.")
        return super().post(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
class UserUpdateView(DashboardLoginRequiredMixin,SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserProfileUpdateForm
    template_name = "dashboard/user_edit.html"
    success_url = reverse_lazy("user_list")
    success_message = "User Edited Successfully."

    def dispatch(self, request, *args, **kwargs):
        user_to_edit = self.get_object()

        if user_to_edit == request.user:
            messages.error(request, "You cannot edit your own account.")
            return redirect("user_list")

        if user_to_edit.role == "admin":
            messages.error(request, "Admin user cannot be edited.")
            return redirect("user_list")

        return super().dispatch(request, *args, **kwargs)

# ===========================
# Category Section
# ===========================
class CategoryCreateView(DashboardLoginRequiredMixin,FormView):
    template_name = "category_form.html"
    form_class = CategoryForm
    success_url = reverse_lazy("category_form")

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Category created successfully!")
        return super().form_valid(form)

class CategoryListView(DashboardLoginRequiredMixin,ListView):
    model = Category
    template_name = "dashboard/categoery_list.html"
    context_object_name = "categoery"
    
class CategoryDeleteView(DashboardLoginRequiredMixin,SuccessMessageMixin, DeleteView):
    model = Category
    success_url = reverse_lazy("categoery_list")
    # success_message = "Product deleted successfully"

    def post(self, request, *args, **kwargs):
        messages.success(request, "Category deleted successfully")
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
class CategoryUpdateView(DashboardLoginRequiredMixin,SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "dashboard/category_edit.html"
    success_url = reverse_lazy("categoery_list")
    success_message = "Category updated successfully!"

    def dispatch(self, request, *args, **kwargs):
        category_to_edit = self.get_object()

        if not category_to_edit:
            messages.error(request, "Category not found.")
            return redirect("categoery_list")

        return super().dispatch(request, *args, **kwargs)

from django.views.generic import ListView
from product.models import Category

class AllCategoryListView(ListView):
    model = Category
    template_name = "dashboard/all_categories_table.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.prefetch_related(
            'subcategories__product_categories'
        )

    
# ===========================
# Product Section
# ===========================
class ProductCreateView(DashboardLoginRequiredMixin,FormView):
    template_name = "dashboard/product_form.html"
    form_class = ProductForm
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Product created successfully!")
        return super().form_valid(form)

class ProductImageCreateView(DashboardLoginRequiredMixin,FormView):
    template_name = "product_image_form.html"
    form_class = ProductImageForm
    success_url = reverse_lazy("product_list")

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

class ProductListView(DashboardLoginRequiredMixin,ListView):
    model = Product
    template_name = "dashboard/product_list.html"
    context_object_name = "products"
    
class ProductDeleteView(DashboardLoginRequiredMixin,SuccessMessageMixin, DeleteView):
    model = Product
    success_url = reverse_lazy("product_list")
    # success_message = "Product deleted successfully"

    def post(self, request, *args, **kwargs):
        messages.success(request, "Product deleted successfully")
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
class ProductUpdateView(DashboardLoginRequiredMixin,UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/product_edit.html"  # Tamaru template path
    success_url = reverse_lazy("product_list")      # Redirect after update
    success_message = "Product updated successfully!"

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

# ===========================
# Banner Section
# ===========================
class BannerView(DashboardLoginRequiredMixin,ListView):
    model = Banner
    template_name = "dashboard/banner_list.html"
    context_object_name = "banners"

class BannerCreateView(DashboardLoginRequiredMixin,SuccessMessageMixin, CreateView):
    model = Banner
    form_class = BannerForm
    template_name = "dashboard/add_banner.html"
    success_url = reverse_lazy("banner")
    success_message = "Banner added successfully"

class BannerDeleteView(DashboardLoginRequiredMixin,SuccessMessageMixin, DeleteView):
    model = Banner
    success_url = reverse_lazy("banner")
    success_message = "Banner deleted successfully"

    # Disable confirmation page
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
class BannerUpdateView(DashboardLoginRequiredMixin,UpdateView):
    model = Banner
    form_class = BannerForm
    template_name = "dashboard/banner_edit.html"  
    success_url = reverse_lazy("banner")
    success_message = "Banner updated successfully!"

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

class BannerStatusToggleView(DashboardLoginRequiredMixin,View):
    def post(self, request, pk):
        banner = get_object_or_404(Banner, pk=pk)
        banner.is_active = not banner.is_active
        banner.save()

        if banner.is_active:
            messages.success(request, "Banner activated successfully")
        else:
            messages.success(request, "Banner deactivated successfully")
        return redirect("banner")


from django.views.generic import ListView
from cart.models import Cart

class CartDashboardView(ListView):
    model = Cart
    template_name = 'dashboard/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return Cart.objects.select_related('user', 'product')


