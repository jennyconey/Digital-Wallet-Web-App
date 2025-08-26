from django.shortcuts import render

from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect

import payapp.views
from payapp.models import Balance
from register.forms import RegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect


# Registers a new user and converts their balance to USD
@csrf_protect
def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            balance = Balance.objects.get(name=user.id)

            currency = form.cleaned_data['currency']
            # Convert user's balance to USD
            converted_balance = payapp.views.convert_currency(currency, balance.balance)

            # Update the balance object with the new converted balance
            balance.balance = converted_balance
            balance.save()
            messages.success(request, "Registration successful.")
            return redirect("login")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = RegisterForm()
    return render(request, "register/register.html", {"register_user": form})


# Allows existing user to log into their account
@csrf_protect
def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, "register/login.html", {"login_user": form})

# Allows user to log out
def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("login")

