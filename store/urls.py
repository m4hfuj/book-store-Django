from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_view, name='store-front'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug:slug>/', views.remove_from_cart, name='remove-from-cart'),

    path('checkout/', views.checkout, name='cart-view'),

    path('order-history/', views.order_history, name='order-history'),
    path('cancel-order/<slug:slug>/', views.cancel_order, name='cancel-order'),
    path('re-order/<slug:slug>/', views.re_order, name='re-order'),

    path('make-return-request/', views.make_return_request, name='make-return-request'),
    path('make-return-request/<int:pk>/', views.make_return_request__item_id),

    # path('return-requests/', views.return_requests, name='return-requests'),
    path('my-return-requests/', views.my_return_requests, name='my-return-requests'),
]
