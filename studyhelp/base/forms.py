from django.forms import ModelForm
from .models import Room
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254, 
        required=True, 
        help_text='Required. Enter a valid email address.'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email