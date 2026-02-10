from django.shortcuts import render
from django.views.generic import TemplateView
from  product.models import *
# Create your views here.
from django.views.generic import TemplateView
from product.models import Product, Banner, SubCategory

class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["banners"] = Banner.objects.filter(is_active=True)

        context["laptops"] = Product.objects.filter(
            sub_category__category__name="Laptop"
        )[:8]

        context["mouses"] = Product.objects.filter(
            sub_category__category__name="Mouse"
        )[:8]

        context["tvs"] = Product.objects.filter(
            sub_category__category__name="TV"
        )[:8]

        context["washing_machines"] = Product.objects.filter(
            sub_category__category__name="Washing Machine"
        )[:8]

        return context


class SubCategoryProductView(TemplateView):
    template_name = "index_2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sub_id = self.kwargs.get("sub_id")
        sort = self.request.GET.get("sort")

        products = Product.objects.filter(sub_category_id=sub_id)

        if sort == "low":
            products = products.order_by("price")
        elif sort == "high":
            products = products.order_by("-price")
        elif sort == "new":
            products = products.order_by("-id")

        context["all_product"] = products
        context["current_subcategory"] = SubCategory.objects.get(id=sub_id)

        return context
