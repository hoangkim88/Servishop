from django.urls import path
from .views import register, login, display_products, search_by_category, get_product, add_to_cart, logout, search_by_name, filter_by_price, get_cart, update_cart, remove_from_cart, stripe_checkout, stripe_success, stripe_cancel, invoice, get_order

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('', display_products, name='display_products'),
    path('search_by_category/<str:category>/', search_by_category, name='search_by_category'),
    path('products/<int:product_id>/', get_product, name='product_details'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('search_by_name/', search_by_name, name='search_by_name'),
    path('filter_by_price/', filter_by_price, name='filter_by_price'),  
    path('get_cart/', get_cart, name='cart'),
    path('update_cart/', update_cart, name='update_cart'),
    path('remove_from_cart/', remove_from_cart, name='remove_from_cart'),
    path('stripe/checkout/', stripe_checkout, name='stripe_checkout'),
    path('checkout/success/', stripe_success, name='stripe_success'),
    path('checkout/cancel/', stripe_cancel, name='stripe_cancel'),
    path('invoice/<str:invoice_id>/', invoice, name='view_invoice'),
    path('get_order/', get_order, name='get_order'),
]
