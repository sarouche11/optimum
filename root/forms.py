
from django import forms
from .models import Category,SubCategory,Product,ActivationCode,Paiement,ProductAchat


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','type_category','image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Name'}),
            'image': forms.ClearableFileInput(attrs={'class':"custom-file-input", 'id':"inputGroupFile01", 'type':"file"}),
            'type_category': forms.Select(attrs={ 'class':"form-control placeholder-select", 'name':"Status","id":"type_category" }),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        original_choices = list(self.fields['type_category'].choices)
        filtered_choices = [choice for choice in original_choices if choice[0] != '']

        # Ajoute ton propre choix vide personnalisé
        self.fields['type_category'].choices = [('', '--- Veuillez sélectionner le type_category ---')] + filtered_choices
       
        self.fields['type_category'].required = False
        self.fields['type_category'].widget.attrs.update({
            'class': 'form-control placeholder-select'
        })



class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'image']

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
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'image': forms.ClearableFileInput(attrs={'class':"custom-file-input", 'id':"inputGroupFile01", 'type':"file"}),
           
        }      

class ActivationCodeForm(forms.ModelForm):
    class Meta:
        model = ActivationCode
        fields = ['code', 'product']

        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code'}),
            
        }    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On filtre les produits pour ne garder que ceux de type CODE
        self.fields['product'].queryset = Product.objects.filter(
            subcategory__category__type_category='code',
            active=True
        )

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['montant']
        widgets = {
            'montant': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Amount'}),
            
        }  



class ProductRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = ProductAchat
        fields = ['answer', 'status','reason']
        widgets = {
            'answer': forms.TextInput(attrs={'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'})
        }


