from django.urls import path
from .views import *


urlpatterns = [

    # Main Category
    path("category/add/", CategoryCreateView.as_view(), name="category_form"),
    path("category/list/", CategoryListView.as_view(), name="categoery_list"),
    path("category/edit/<int:pk>/", CategoryUpdateView.as_view(), name="category_edit"),
    path("category/delete/<int:pk>/", CategoryDeleteView.as_view(), name="category_delete"),

    # SubCategory
    path("subcategory/add/", SubCategoryCreateView.as_view(), name="subcategory_add"),
    path("subcategory/list/", SubCategoryListView.as_view(), name="subcategory_list"),
    path("subcategory/edit/<int:pk>/", SubCategoryUpdateView.as_view(), name="subcategory_edit"),
    path("subcategory/delete/<int:pk>/", SubCategoryDeleteView.as_view(), name="subcategory_delete"),

    
    path("add/", ProductCreateView.as_view(), name="add_product"),
    path("image/add/", ProductImageCreateView.as_view(), name="add_product_image"),
    path("list/", ProductListView.as_view(), name="product_list"),    

]
