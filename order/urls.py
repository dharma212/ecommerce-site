from django.urls import path
from .views import CheckoutView, MyOrdersView, OrderDetailView, PaymentView, OrderStatusView, ReOrderView,CancelOrderView,InvoiceDownloadView
urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('my-orders/', MyOrdersView.as_view(), name='my_orders'),
    path('payment/', PaymentView.as_view(), name='payment'), 
    path('my-orders/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:order_id>/status/', OrderStatusView.as_view(), name='order-status'),
    path('reorder/<int:order_id>/',ReOrderView.as_view(),name='reorder'),
    path('cancel/<int:order_id>/', CancelOrderView.as_view(), name='cancel_order'),
    path("invoice/<int:order_id>/",InvoiceDownloadView.as_view(),name="download_invoice"),
    path("order/<int:order_id>/cancel/",CancelOrderView.as_view(),name="cancel_order"),
    
]