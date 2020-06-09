from django import forms

CONTRY_CHOICES = (
    ('T', 'Togo'),
    ('G', 'Ghana')
)

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)
class CheckoutForm(forms.Form):
    street_address = forms.CharField( widget=forms.TextInput(
        attrs ={
            'placeholder':'234 Lome-tokoin',
            'class':'form-control'
        }
    ))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(
        attrs={
            'placeholder':'2Fr Hotel apartment 435',
            'class':'form-control'
        }
    ))
    contry = forms.ChoiceField(choices=CONTRY_CHOICES)
    zip = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':'form-control'
        }
    ))
    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES
    )
