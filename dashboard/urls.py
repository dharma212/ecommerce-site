from django.urls import path
from dashboard.views import *


urlpatterns = [

    # ================= DASHBOARD =================
    path("", DashboardIndexView.as_view(), name="dashboard_index"),

    # ================= CATEGORY ==================
    path("category/add/", CategoryCreateView.as_view(), name="category_form"),
    path("categories/", CategoryListView.as_view(), name="categoery_list"),
    path("category/edit/<int:pk>/", CategoryUpdateView.as_view(), name="category_edit"),
    path("category/delete/<int:pk>/", CategoryDeleteView.as_view(), name="category_delete"),

    # ================= SubCategory ===============
    path("subcategory/add/", SubCategoryCreateView.as_view(), name="subcategory_add"),
    path("subcategory/list/", SubCategoryListView.as_view(), name="subcategory_list"),
    path("subcategory/edit/<int:pk>/", SubCategoryUpdateView.as_view(), name="subcategory_edit"),
    path("subcategory/delete/<int:pk>/", SubCategoryDeleteView.as_view(), name="subcategory_delete"),

    # ================= PRODUCTS ==================
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/add/", ProductCreateView.as_view(), name="add_product"),
    path("products/add/images/",ProductImageCreateView.as_view(),name="add_product_image"),
    path("product/delete/<int:pk>/",ProductDeleteView.as_view(),name="product_delete"),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path("order/cancle-orders/",AdminCancleOrderListView.as_view(),name="cancle_orders"),



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
    
    path('cart/', CartDashboardView.as_view(), name='cart_dashboard'),
    path("dashboard/wishlist/", WishlistDashboardView.as_view(), name="wishlist_dashboard"),
    path('contactus/list',ContactListView.as_view(),name="contactus"),
    path('dashboard/orders/', AdminOrderListView.as_view(), name='admin_order_list'),
    path('dashboard/orders/<int:pk>/update/', AdminOrderUpdateView.as_view(), name='admin_order_update'),
    path("pending-calendar/",PendingOrderCalendarView.as_view(),name="admin_pending_calendar"),
    path("dashboard/pending-calendar-events/",PendingOrderCalendarEvents.as_view(),name="pending_calendar_events"),
    path("dashboard/ajax/pending-hour-events/",PendingOrderHourEvents.as_view(),name="pending_hour_events"),
]
