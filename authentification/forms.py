from django import forms
from captcha.fields import CaptchaField
from .models import Profile, User
import re


class CaptchaForm(forms.Form):
    captcha = CaptchaField()



class ProfileForm(forms.ModelForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Username"})
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "First Name"})
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Last Name"})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Email"})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Password"})
    )

    captcha = CaptchaField() 

    class Meta:
       
        model = Profile
        fields = ['adresse', 'phone']

        widgets = {
                   'adresse': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Address'}),
                   'phone': forms.TextInput(attrs={'class': 'form-control','placeholder': '0xxxxxxxxx', 'maxlength': '10'}),
        }


    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")

        return username

    # ✅ VALIDATION EMAIL
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")

        return email

    # ✅ VALIDATION PHONE
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not re.match(r'^0\d{9}$', phone):
            raise forms.ValidationError(
                "The phone number must start with 0 and contain exactly 10 digits."
            )

        if Profile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already in use.")

        return phone