from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, UserActivityLog, Review

# 1. Kategoriler
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# 2. Ürünler (Resim önizlemeli olabilir ama şimdilik temel bilgiler)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_active') # Listeden direkt düzenleme imkanı!
    prepopulated_fields = {'slug': ('name',)}

# 3. Siparişler
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at')
    list_filter = ('created_at',)
    inlines = [OrderItemInline] # Siparişin içine girince ürünleri de göster

# 4. Güvenlik Logları (Blue Team Özel - Read Only)
@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'timestamp')
    list_filter = ('action',)
    search_fields = ('user__username', 'ip_address', 'description')
    
    # Loglar değiştirilemez, sadece okunur! (Delil karartmayı önlemek için)
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

# 5. Yorumlar
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('subject', 'product', 'user', 'rating', 'status')
    list_filter = ('status', 'rating')
    list_editable = ('status',) # Yorumu hızlıca onayla/reddet

admin.site.register(Cart)
# CartItem genelde admin panelinde çok kurcalanmaz ama eklenebilir.