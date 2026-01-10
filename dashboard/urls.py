from django.urls import path
from dashboard.views import *

urlpatterns = [

    # ================= DASHBOARD =================
    path("", DashbboardIndexView.as_view(), name="dashboard_index"),
    # path("login/", CustomLoginView.as_view(), name="login"),  # ✅ proper login URL


    # ================= CATEGORY ==================
    path("category/add/", CategoryCreateView.as_view(), name="category_form"),
    path("categories/", AllCategory.as_view(), name="categoery_list"),
    path("category/delete/<int:pk>/",CategoryDeleteView.as_view(),name="category_delete"),
    path('categories/edit/<int:pk>/', CategoryUpdateView.as_view(), name='category_edit'),

        

    # ================= PRODUCTS ==================
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/add/", ProductCreateView.as_view(), name="add_product"),
    path("products/add/images/",ProductImageCreateView.as_view(),name="add_product_image"),
    path("product/delete/<int:pk>/",ProductDeleteView.as_view(),name="product_delete"),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),


    # ================= BANNERS ===================
    path("banners/", BannerView.as_view(), name="banner"),
    path("banners/add/", BannerCreateView.as_view(), name="Add_banner"),
    path("banners/delete/<int:pk>/", BannerDeleteView.as_view(), name="banner_delete"),
    path('banner/<int:pk>/edit/', BannerUpdateView.as_view(), name='banner_edit'),
    path("banners/toggle/<int:pk>/", BannerStatusToggleView.as_view(), name="banner_toggle"),


    # ================= USERS =====================
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/add/", UserCreateView.as_view(), name="add_user"),
    path("users/delete/<int:pk>/", UserDeleteView.as_view(), name="user_delete"),
    path("users/edit/<int:pk>/", UserUpdateView.as_view(), name="user_edit"),
]
