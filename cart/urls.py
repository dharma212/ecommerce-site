from django.urls import path
from .views import AddToCartView, CartListView, AddToCartAjaxView


urlpatterns = [
    path('', CartListView.as_view(), name='cart_list'),
    path('add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path("add/ajax/", AddToCartAjaxView.as_view(), name="add_to_cart_ajax"),

]
