
from django import forms
from .models import Category,SubCategory,Product,ActivationCode,Paiement


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','image', 'active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Name'}),
            'image': forms.ClearableFileInput(attrs={'class':"custom-file-input", 'id':"inputGroupFile01", 'type':"file"}),
           
        }



class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'image', 'active']

        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom sous-catégorie'}),
            'image': forms.ClearableFileInput(attrs={'class':"custom-file-input", 'id':"inputGroupFile01", 'type':"file"}),
            
        }      

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['subcategory', 'price','name', 'image', 'active']

        widgets = {
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nom sous-catégorie'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom sous-catégorie'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Nom sous-catégorie'}),
            'image': forms.ClearableFileInput(attrs={'class':"custom-file-input", 'id':"inputGroupFile01", 'type':"file"}),
           
        }      

class ActivationCodeForm(forms.ModelForm):
    class Meta:
        model = ActivationCode
        fields = ['code', 'product']

        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom sous-catégorie'}),
            
        }    

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['montant']
        widgets = {
            'montant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Montant'}),
            
        }  