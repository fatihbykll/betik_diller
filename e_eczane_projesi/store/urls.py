from django.urls import path
from . import views

urlpatterns = [
    # 1. Ana Sayfa
    path('', views.product_list, name='product_list'),
    
    # 2. Kategori Sayfası
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),

    # 3. Yardımcı Sayfalar (Sepet, Checkout vs.)
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('my-orders/', views.order_history, name='order_history'),
    path('register/', views.register, name='register'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),

    # 4. Ürün Detay Sayfası (DİKKAT: En sona koyduk ve İKİ parametre alıyor)
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]