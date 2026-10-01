from django import forms
from .models import Customer

class CustomerEditForm(forms.ModelForm):
    Customer_name = forms.CharField(
        label='得意先名',
        max_length=32,
        required=True
    )

    discount_rate = forms.IntegerField(
        label='割引率(%)',
        min_value=0,
        max_value=99,
        required=True
    )

    class Meta:
        model = Customer
        fields = [
            'customer_name',
            'customer_telno',
            'customer_postalcode',
            'customer_address',
            'discount_rate',
        ]

        labels = {
            'customer_telno':'電話番号',
            'customer_postalcode':'郵便番号',
            'customer_address':'住所',
        }