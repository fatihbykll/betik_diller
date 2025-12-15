from django.db import models
from django.contrib.auth.models import User

# 1. Kategori Modeli
class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Kategori Adı")
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Kategoriler'

    def __str__(self):
        return self.name

# 2. Ürün Modeli
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name="Ürün Adı")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL Yolu") 
    description = models.TextField(blank=True, verbose_name="Açıklama")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    stock = models.IntegerField(default=0, verbose_name="Stok Adedi")
    image = models.ImageField(upload_to='products/', blank=True, verbose_name="Ürün Resmi")
    is_active = models.BooleanField(default=True, verbose_name="Satışta mı?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Ürünler'

    def __str__(self):
        return self.name
    
    def average_review(self):
        reviews = self.reviews.filter(status=True).aggregate(average=models.Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def count_review(self):
        reviews = self.reviews.filter(status=True).aggregate(count=models.Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

# 3. Sepet (Cart) Modeli
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True, verbose_name="Sepet ID") 
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.cart_id)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

# 4. Sepet Ürünü (CartItem) Modeli
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity
    # store/models.py dosyasının en altı

# 5. Sipariş (Order) Modeli - Siparişin başlığı
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sipariş Tarihi")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Toplam Tutar")

    def __str__(self):
        return f"Sipariş #{self.id} - {self.user.username}"

# 6. Sipariş Detayı (OrderItem) - Siparişin içindeki ürünler
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Satış Fiyatı") # O anki fiyatı kaydetmek kritik!

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

# store/models.py dosyasının en altı

# 7. Güvenlik Logları (Audit Log)
class UserActivityLog(models.Model):
    ACTION_CHOICES = (
        ('LOGIN', 'Giriş Yaptı'),
        ('LOGOUT', 'Çıkış Yaptı'),
        ('REGISTER', 'Kayıt Oldu'),
        ('ADD_CART', 'Sepete Ekleme'),
        ('REMOVE_CART', 'Sepetten Silme'),
        ('ORDER', 'Sipariş Verme'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Kullanıcı silinse bile log kalsın (Blue Team kuralı)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="İşlem Türü")
    description = models.TextField(verbose_name="Açıklama")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Zaman")

    def __str__(self):
        return f"{self.user} - {self.action} ({self.timestamp})"
        
    class Meta:
        verbose_name = 'Kullanıcı Logu'
        verbose_name_plural = 'Kullanıcı Hareketleri & Güvenlik Logları'
        ordering = ['-timestamp'] # En yeniden eskiye sırala    

# 8. Yorum ve Puanlama Sistemi
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True, verbose_name="Başlık")
    review = models.TextField(max_length=500, blank=True, verbose_name="Yorum")
    rating = models.FloatField(verbose_name="Puan")
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    is_updated = models.BooleanField(default=False, verbose_name="Düzenlendi mi?") 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject       
