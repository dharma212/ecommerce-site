from django.shortcuts import render
from django.views.generic import TemplateView
from  product.models import *
# Create your views here.
class IndexView(TemplateView):
    template_name="index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_product=Product.objects.all()
        # banner=Banner.objects.all()
        context["all_product"] =all_product
        context["banners"] = Banner.objects.filter(is_active=True)
        return context