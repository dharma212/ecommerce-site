from django.urls import path
from .views import CheckoutView, MyOrdersView, OrderDetailView, PaymentView, get_order_status

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('my-orders/', MyOrdersView.as_view(), name='my_orders'),
    path('payment/', PaymentView.as_view(), name='payment'), 
    path('my-orders/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('get-status/<int:order_id>/', get_order_status, name='get_status'),
]