from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Product, Cart, CartItem, Order, OrderItem, UserActivityLog, Review
from .forms import ReviewForm , RegisterForm


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()  # Oturumu oluştur
        cart = request.session.session_key  # Şimdi anahtarı al
    return cart

# --- YARDIMCI FONKSİYON: IP ADRESİ BULMA ---
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# 1. Ana Sayfa (Ürün Listesi + Kategori Filtreleme + Arama)
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all() 
    products = Product.objects.filter(is_active=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    context = {
        'products': products,
        'categories': categories,
        'category': category,
        'search_query': search_query
    }
    return render(request, 'store/product_list.html', context)

# 2. Kayıt Olma (Loglama Eklendi)
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # --- GÜVENLİK LOGU ---
            # Kayıt olan kullanıcıyı loglayalım
            UserActivityLog.objects.create(
                user=user,
                action='REGISTER',
                description="Kullanıcı sisteme kayıt oldu.",
                ip_address=get_client_ip(request)
            )
            
            login(request, user) # Kayıt olunca otomatik giriş yapsın
            messages.success(request, "Aramıza hoşgeldin! Kayıt başarıyla tamamlandı.")
            return redirect('product_list')
        else:
            messages.error(request, "Bir hata oluştu. Lütfen bilgileri kontrol edin.")
    else:
        form = RegisterForm()
    
    context = {
        'form': form
    }
    return render(request, 'registration/register.html', context)

# 3. Sepete Ekleme (Loglama Eklendi)
@login_required(login_url='/accounts/login/')
def add_to_cart(request, product_id):
    current_user = request.user
    product = get_object_or_404(Product, id=product_id)

    # --- 1. STOK KONTROLÜ (Stok yoksa Ürün Sayfasında Kal) ---
    if product.stock <= 0:
        messages.error(request, 'Bu ürün stokta kalmadı!')
        # Hata verince Sepete DEĞİL, tekrar ürün sayfasına dönüyoruz:
        return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)

    # --- 2. SEPET MANTIĞI ---
    try:
        # Sepeti bulmaya çalış, yoksa oluştur
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        # Stoktan fazla eklemeyi engelle
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Ürün sepete eklendi.')
        else:
            messages.warning(request, 'Stoktaki tüm ürünleri zaten eklediniz.')
            
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()
        messages.success(request, 'Ürün sepete eklendi.')
    
    # İşlem başarılıysa SEPETİM sayfasına git
    return redirect('cart_detail')

# 4. Sepet Detayı
@login_required(login_url='/accounts/login/')
def cart_detail(request, total=0, quantity=0, cart_items=None):
    try:
        # 1. Sepeti Bul
        cart = Cart.objects.get(cart_id=_cart_id(request))
        
        # 2. Sepetteki Ürünleri Getir 
        # (DÜZELTME: is_active=True kısmını kaldırdık çünkü CartItem modelinde böyle bir alan yok)
        cart_items = CartItem.objects.filter(cart=cart)
        
        # 3. Toplam Fiyat ve Adet Hesapla
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

    except Cart.DoesNotExist: 
        # (DÜZELTME: ObjectDoesNotExist yerine Cart.DoesNotExist kullandık, import gerekmez)
        pass 

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart_detail.html', context)

# 5. Sepetten Silme (Loglama Eklendi)
@login_required(login_url='/accounts/login/')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # Güvenlik Kontrolü
    if cart_item.cart.user == request.user:
        product_name = cart_item.product.name # Silmeden önce ismini alalım
        cart_item.delete()
        
        # --- LOG EKLE ---
        UserActivityLog.objects.create(
            user=request.user, 
            action='REMOVE_CART', 
            description=f"{product_name} sepetten silindi.", 
            ip_address=get_client_ip(request)
        )
        
    return redirect('cart_detail')

# 6. Ödeme (Checkout) ve Stok Düşme (Loglama Eklendi)
@login_required(login_url='/accounts/login/')
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart or not cart.items.exists():
        messages.error(request, "Sepetiniz boş.")
        return redirect('product_list')

    # Sipariş Kaydı
    order = Order.objects.create(user=request.user, total_price=0)
    final_total = 0

    for item in cart.items.all():
        if item.product.stock >= item.quantity:
            item.product.stock -= item.quantity
            item.product.save()
            
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            final_total += item.total_price
        else:
            order.delete()
            messages.error(request, f"{item.product.name} için yeterli stok kalmadı.")
            return redirect('cart_detail')
    
    order.total_price = final_total
    order.save()
    
    cart.items.all().delete()
    
    # --- LOG EKLE ---
    UserActivityLog.objects.create(
        user=request.user, 
        action='ORDER', 
        description=f"Sipariş verildi. Tutar: {order.total_price} TL. Sipariş ID: {order.id}", 
        ip_address=get_client_ip(request)
    )
    
    messages.success(request, f"Siparişiniz alındı! Sipariş No: #{order.id}")
    return redirect('order_success')

# 7. Sipariş Başarılı Ekranı
def order_success(request):
    return render(request, 'store/order_success.html')

# 8. Sipariş Geçmişi
@login_required(login_url='/accounts/login/')
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})

# store/views.py içindeki product_detail fonksiyonu TAM OLARAK böyle olmalı:

def product_detail(request, category_slug, product_slug):
    # 1. Ürünü Bul
    product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)

    # 2. Sepet Kontrolü (Hata vermeyen yöntem)
    in_cart = False
    try:
        # Cart ID'ye göre sepeti bul
        cart = Cart.objects.get(cart_id=_cart_id(request))
        # Ürün sepette mi?
        in_cart = CartItem.objects.filter(cart=cart, product=product).exists()
    except Cart.DoesNotExist:
        in_cart = False

    # 3. Yorumları Getir
    reviews = Review.objects.filter(product=product, status=True)

    # 4. Satın Alma ve Yorum Kontrolü
    user_bought = False
    user_review = None

    if request.user.is_authenticated:
        # Bu kullanıcı ürünü sipariş etmiş mi?
        user_bought = OrderItem.objects.filter(order__user=request.user, product=product).exists()
        # Daha önce yorum yapmış mı?
        user_review = Review.objects.filter(user=request.user, product=product).first()

    context = {
        'product': product,
        'in_cart': in_cart,
        'reviews': reviews,
        'user_bought': user_bought,
        'user_review': user_review,
    }
    return render(request, 'store/product_detail.html', context)


@login_required(login_url='/accounts/login/')
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER') # Kullanıcıyı geldiği sayfaya geri göndermek için
    if request.method == 'POST':
        try:
            # --- GÜVENLİK KONTROLÜ BAŞLANGICI ---
            # Kullanıcı bu ürünü daha önce sipariş etmiş mi?
            # OrderItem tablosunda bu kullanıcıya ait siparişlerde bu ürün var mı diye bakıyoruz.
            has_bought = OrderItem.objects.filter(
                order__user=request.user, 
                product__id=product_id
            ).exists()

            if not has_bought:
                messages.error(request, "Bu ürünü değerlendirmek için önce satın almalısınız.")
                return redirect(url)
            # --- GÜVENLİK KONTROLÜ BİTİŞİ ---

            # Eğer satın almışsa, yorumu kaydetmeye devam et:
            reviews = Review.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, "Yorumunuz güncellendi.")
            return redirect(url)

        except Review.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, "Yorumunuz başarıyla gönderildi.")
                return redirect(url)