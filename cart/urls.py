from django.urls import path
from .views import *

urlpatterns = [
  path('', CartListView.as_view(), name='cart_list'),
  path('add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
  path('ajax/add/', AddToCartAjaxView.as_view(), name='add_to_cart_ajax'),
  path('ajax/remove/', RemoveFromCartAjaxView.as_view(), name='remove_from_cart_ajax'),
  path('ajax/update-qty/', UpdateCartQtyAjaxView.as_view(), name='update_cart_qty'),

  path('wishlist/', WishlistListView.as_view(), name='wishlist_list'),
  path("wishlist/ajax/toggle/", WishlistToggleAjaxView.as_view(), name="wishlist_toggle"),
  path('wishlist/ajax/toggle/', ToggleWishlistView.as_view(), name='toggle-wishlist-ajax'),
  path('ajax/get_items/', GetCartWishlistView.as_view(), name='get-cart-wishlist'),
 path("ajax/wishlist/remove/",RemoveFromWishlistAjaxView.as_view(),name="wishlist_remove",),  
path(
    "wishlist/move-to-cart/",
    MoveWishlistToCartView.as_view(),
    name="move_wishlist_to_cart"
),
    path('cart/count/', CartCountView.as_view(), name='cart_count'),

]