from django.urls import path
from . import views

urlpatterns = [
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('manage_product/', views.manage_product, name='manage_product'),
    path('manage_order/', views.manage_order, name='manage_order'),
    path('add_product/', views.add_product, name='add_product'),
    path('save_product/', views.save_product, name='save_product'),
    path('products/<int:product_id>/update', views.update_product, name='update_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
]
