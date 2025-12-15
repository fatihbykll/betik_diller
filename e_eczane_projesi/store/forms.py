from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review

# 1. Yorum Yapma Formu
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['subject', 'review', 'rating']

# 2. Kayıt Olma Formu (Düzeltilmiş ve Özelleştirilmiş)
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Adınız", required=True)
    last_name = forms.CharField(label="Soyadınız", required=True)
    email = forms.EmailField(label="E-Posta Adresi", required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        
        # Tüm alanlara Bootstrap class'ı ekle
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
        # Etiket düzeltmeleri
        self.fields['username'].label = "Kullanıcı Adı"
        self.fields['username'].help_text = ""