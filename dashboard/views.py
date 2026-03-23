# ===========================
# Django Core Imports
# ===========================
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import (TemplateView,FormView,ListView,CreateView,DeleteView,UpdateView)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.contrib import messages
from users.forms import UserProfileUpdateForm,UserForm
from django.contrib.auth.views import LoginView
from cart.models import Cart
from order.models import Order
# ===========================
# Models Imports
# ===========================
from users.models import *
from product.models import *
from django.db.models import Count
from cart.models import *
# ===========================
# Forms Imports
# ===========================
from product.forms import *
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, F,Q
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from order.models import Order  
from django.contrib.auth import get_user_model
from django.db.models import Sum


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
User = get_user_model()

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Q
from django.utils import timezone

User = get_user_model()

from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

class DashboardIndexView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Existing stats (UNCHANGED)
        total_users = User.objects.count()
        total_sales = Order.objects.filter(status='Delivered')\
            .aggregate(Sum('total_price'))['total_price__sum'] or 0
        pending_orders_count = Order.objects.filter(status='Pending').count()

        admins = User.objects.filter(is_staff=True).count()
        customers = total_users - admins

        # 🔹 TOP SELLING PRODUCTS (by quantity sold)
        top_products = (
            Product.objects.annotate(
                sales_count=Sum(
                    'orderitem__quantity',
                    filter=Q(orderitem__order__status='Delivered')
                )
            )
            .filter(sales_count__gt=0)
            .order_by('-sales_count')[:5]
        )

        # 🔹 ORDERS LAST 7 DAYS (day-wise)
        today = timezone.now().date()
        last_7_days = today - timedelta(days=6)

        orders_by_day = (
            Order.objects
            .filter(created_at__date__gte=last_7_days)
            .extra(select={'day': "DATE(created_at)"})
            .values('day')
            .annotate(total=Count('id'))
            .order_by('day')
        )

        context.update({
            'total_users': total_users,
            'total_sales': total_sales,
            'pending_orders_count': pending_orders_count,
            'customers': customers,
            'admins': admins,
            'top_products': top_products,
            'orders_by_day': orders_by_day,
            'recent_orders': Order.objects.order_by('-created_at')[:5],
        })

        return context
    
    

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from order.models import Order

class DashboardView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "dashboard.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).select_related("invoice")

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

class SubCategoryCreateView(LoginRequiredMixin, FormView):
    model = SubCategory
    template_name = "dashboard/subcategory_form.html"
    form_class = SubCategoryForm
    success_url = reverse_lazy("subcategory_list")

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
    success_url = reverse_lazy("subcategory_list")

    def form_valid(self, form):
        messages.success(self.request, "Sub Category updated successfully!")
        return super().form_valid(form)

class SubCategoryDeleteView(DeleteView):
    model = SubCategory
    success_url = reverse_lazy("subcategory_list")

    def post(self, request, *args, **kwargs):
        messages.success(request, "Sub Category deleted successfully!")
        return super().post(request, *args, **kwargs)

    
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

    def post(self, request, *args, **kwargs):
        messages.success(request, "Product deleted successfully")
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
        
class ProductUpdateView(DashboardLoginRequiredMixin,UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/product_edit.html" 
    success_url = reverse_lazy("product_list")      
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


class CartDashboardView(ListView):
    model = Cart
    template_name = 'dashboard/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return (
            Cart.objects
            .select_related('user', 'product')
            .order_by('-created_at')
        )

class WishlistDashboardView(ListView):
    model = Wishlist
    template_name = "dashboard/wishlist.html"
    context_object_name = "wishlist_items"

    def get_queryset(self):
        return (
            Wishlist.objects
            .select_related("user", "product")
            .order_by("-created_at")
        )

class ContactListView(ListView):
    model = Contact
    template_name = "dashboard/contactus-list.html"
    context_object_name = "contacts"
    ordering = ["-created_at"]
    
class AdminOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'dashboard/order-list.html' 
    context_object_name = 'orders'
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.annotate(items_count=Count('items')).filter(items_count__gt=0).order_by('-created_at')


class AdminCancleOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'dashboard/cancle_order.html' 
    context_object_name = 'orders'
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.filter(status__iexact="Cancelled").order_by('-created_at')

class AdminOrderUpdateView(DashboardLoginRequiredMixin, UpdateView):
    model = Order
    fields = ['status']
    template_name = 'dashboard/admin_order_update.html'
    success_url = reverse_lazy('admin_order_list') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.get_object()
        return context
    
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from datetime import date
# from .models import Order

class PendingOrderCalendarView(TemplateView):
    template_name = "dashboard/pending_orders.html"

    
from django.views import View
from django.http import JsonResponse
# from .models import Order

class PendingOrderCalendarEvents(View):
    def get(self, request, *args, **kwargs):

        orders = (
            Order.objects
            .filter(status__iexact="Pending")
            .values("created_at")
        )

        date_count = {}

        for o in orders:
            date = o["created_at"].date()   # convert datetime → date
            date_count[date] = date_count.get(date, 0) + 1

        events = [
            {
                "title": f"Pending Orders: {count}",
                "start": str(date),   # MUST be string YYYY-MM-DD
                "allDay": True,
            }
            for date, count in date_count.items()
        ]

        return JsonResponse(events, safe=False)
    
# views.py
from django.views import View
from django.http import JsonResponse
from django.db.models.functions import TruncHour
from django.db.models import Count
from order.models import Order

class PendingOrderHourEvents(View):
    def get(self, request, *args, **kwargs):

        orders = (
            Order.objects
            .filter(status="Pending")
            .annotate(hour=TruncHour("created_at"))
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("hour")
        )

        events = []
        for o in orders:
            events.append({
                "title": f"{o['count']} Pending Orders",
                "start": o["hour"].isoformat(),  # IMPORTANT
                "allDay": False,
            })

        return JsonResponse(events, safe=False)
    
      
from django.views import View
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from order.models import Invoice       
        
class InvoiceDownloadView(View):
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)

        if not invoice.invoice_file:
            raise Http404("Invoice file not found")

        return FileResponse(
            invoice.invoice_file.open('rb'),
            as_attachment=True,
            filename=f"{invoice.invoice_number}.pdf"
        )
        
from django.views import View
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from order.models import Invoice

class DownloadInvoiceView(LoginRequiredMixin, View):

    def get(self, request, pk):
        invoice = get_object_or_404(
            Invoice,
            pk=pk,
            order__user=request.user
        )

        return FileResponse(
            invoice.invoice_file.open(),
            as_attachment=True,
            filename=invoice.invoice_file.name
        )
        
class DashboardCouponListView(ListView):
    model = Coupon
    template_name = 'dashboard/admin_coupon.html'
    context_object_name = 'coupons'
    
class CouponCreateView(CreateView):
    model = Coupon
    template_name = 'dashboard/add_coupon.html'
    success_url = reverse_lazy('dashboard_coupons')

    fields = [
        'code',
        'discount_type',
        'discount_value',
        'min_amount',
        'valid_from',
        'valid_to',
        'active'
    ]
    
class ToggleCouponView(View):
    def get(self, request, pk):
        coupon = get_object_or_404(Coupon, pk=pk)
        coupon.active = not coupon.active
        coupon.save()
        return redirect('dashboard_coupons')
    
class DeleteCouponView(View):
    def post(self, request, pk):
        coupon = get_object_or_404(Coupon, pk=pk)
        coupon.delete()
        return redirect('dashboard_coupons')