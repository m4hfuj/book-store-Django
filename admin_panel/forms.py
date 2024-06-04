from django import forms
from store.models import Product, Inventory


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'discount', 'bonus']


# class InventoryForm(forms.ModelForm):
#     class Meta:
#         model = Inventory
#         fields = ['product', 'quantity']