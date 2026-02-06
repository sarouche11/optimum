from django import forms
from captcha.fields import CaptchaField
from .models import Profile, User
import re
from django.contrib.auth.forms import PasswordChangeForm



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
    



class ProfileEditForm(forms.ModelForm):
    # Champs liés à User
 
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "First Name"})
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Last Name"})
    )

    


    class Meta:
        model = Profile
        fields = ['phone', 'adresse']  

        widgets = {
                   'adresse': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Address'}),
                   'phone': forms.TextInput(attrs={'class': 'form-control','placeholder': '0xxxxxxxxx', }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name




class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Modifier les labels
        self.fields['old_password'].label = "Mot de passe actuel"
        self.fields['new_password1'].label = "Nouveau mot de passe"
        self.fields['new_password2'].label = "Confirmez le nouveau mot de passe"

        # Ajouter des placeholders
        self.fields['old_password'].widget.attrs.update({'placeholder': 'Entrez votre mot de passe actuel'})
        self.fields['new_password1'].widget.attrs.update({'placeholder': 'Entrez le nouveau mot de passe'})
        self.fields['new_password2'].widget.attrs.update({'placeholder': 'Confirmez le nouveau mot de passe'})

        # Ajouter des classes CSS pour le style (Bootstrap / Material)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})