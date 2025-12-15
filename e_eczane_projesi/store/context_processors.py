from .models import Cart

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        # Kullanıcının sepetini bul, yoksa hata verme
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            # Sepetteki tüm ürünlerin adetlerini topla (Örn: 2 Aspirin + 1 Vitamin = 3)
            count = sum(item.quantity for item in cart.items.all())
    
    return {'cart_item_count': count}