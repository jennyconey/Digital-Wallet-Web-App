from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from . import models


class BalanceTransferForm(forms.Form):
    enter_destination_username = forms.CharField(label="Enter destination username", max_length=100)
    enter_amount_to_transfer = forms.DecimalField(label="Enter amount to transfer", max_digits=10)


class PaymentRequestForm(forms.Form):
    enter_destination_username = forms.CharField(label="Enter destination username", max_length=100)
    enter_amount_to_request = forms.DecimalField(label="Enter amount to request", max_digits=10)


class RespondToRequestForm(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput())
    action = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'respond_to_request'
        self.helper.add_input(Submit('submit', 'Respond', css_class='btn-primary'))