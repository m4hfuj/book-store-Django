from django.urls import path
from . import views

urlpatterns = [
    path('return-requests/', views.return_requests, name='return_requests'),

    path('rr-accept/<slug:slug>/', views.rr_accept, name='rr_accept'),
    path('rr-reject/<slug:slug>/', views.rr_reject, name='rr_reject'),

    path('all-order-history/', views.all_order_history, name='all_order_history'),
    path('deliver-product/<slug:slug>/', views.deliver_product, name='deliver_product'),

    path('users/', views.users_view, name='users_view'),

    path('product/list/', views.product_list, name='product_list'),
    path('product/new/', views.product_create, name='product_create'),

    path('product/<slug:slug>/edit/', views.product_update, name='product_update'),
    # path('product/<slug:slug>/delete/', views.product_delete, name='product_delete'),
    
    path('category/create/', views.author_create, name='category_create'),

    # path('admin/', name= 'admin_settings'),
]