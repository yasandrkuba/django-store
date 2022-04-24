from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('L', 'LiqPay (not available yet)'),
    ('С', 'C.O.D'),
)


class ReportForm(forms.Form):
    message = forms.CharField(label='Report details', widget=forms.Textarea(attrs={
        'rows': 4,
    }))
    full_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    phone_number = forms.CharField()
    email = forms.EmailField()
    ref_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4,
    }))
    phone_number = forms.CharField()
    email = forms.EmailField()


class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'youremail@example.com',
        'class': 'form-control',
    }))
    phone_number = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'London, 1234 Main St',
        'class': 'form-control',
    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(
           attrs={"class": "custom-select d-block w-100"}
        ))
    zip = forms.CharField(max_length=9, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    same_shipping_address = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'custom-control-input',
    }))
    save_info = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'custom-control-input',
    }))
    payment_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)
