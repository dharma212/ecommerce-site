from django.urls import path
from .views import (CategoryCreateView,ProductCreateView,ProductImageCreateView,ProductListView)

app_name = "product" 

urlpatterns = [
    path("category/add/", CategoryCreateView.as_view(), name="category_form"),
    path("add/", ProductCreateView.as_view(), name="add_product"),
    path("image/add/", ProductImageCreateView.as_view(), name="add_product_image"),
    path("list/", ProductListView.as_view(), name="product_list"),    
]
