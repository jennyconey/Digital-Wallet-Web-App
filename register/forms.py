from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from payapp.models import Balance


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    balance = forms.DecimalField()
    currency = forms.ChoiceField(choices=[
        ('GBP', 'British Pounds'),
        ('USD', 'US Dollars'),
        ('EUR', 'Euros'),
    ])

    class Meta:
        model = User
        fields = ("username", "balance", "currency", "email", "password1", "password2")

    def save(self, *args, **kwargs):
        instance = super(RegisterForm, self).save(*args, **kwargs)
        Balance.objects.create(name=instance, balance=self.cleaned_data['balance'])
        return instance
