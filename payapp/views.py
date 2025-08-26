from django.utils import timezone

from django.shortcuts import render, redirect, HttpResponse
from django.db import transaction, OperationalError
from django.db.models import F
from django.shortcuts import render
from . import models
from .context_processor import request_payment_list
from .forms import BalanceTransferForm, PaymentRequestForm, RespondToRequestForm
from .models import Balance, PaymentRequest, TransferRecord
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.contrib.auth.models import User


# Allows user to send payment to another user
@transaction.atomic
def balance_transfer(request):
    if request.method == 'POST':
        form = BalanceTransferForm(request.POST)

        if form.is_valid():

            src_username = request.user.username
            dst_username = form.cleaned_data["enter_destination_username"]
            amount_to_transfer = form.cleaned_data["enter_amount_to_transfer"]

            # Check if the user is trying to send money to themselves
            if src_username == dst_username:
                messages.error(request, "You cannot send money to yourself.")
                return render(request, "payapp/send_money.html", {"form": form})


            src_balance = models.Balance.objects.select_related().get(name__username=src_username)
            dst_balance = models.Balance.objects.select_related().get(name__username=dst_username)

            # Check if the user has sufficient funds
            if src_balance.balance < amount_to_transfer:
                messages.error(request, "Insufficient funds.")
                return render(request, "payapp/send_money.html", {"form": form})

            try:
                with transaction.atomic():
                    # Update the balances of both users
                    src_balance.balance = src_balance.balance - amount_to_transfer
                    src_balance.save()
                    dst_balance.balance = dst_balance.balance + amount_to_transfer
                    dst_balance.save()
            except models.Balance.DoesNotExist:
                messages.error(request, "Source or destination user does not exist.")
                return render(request, "payapp/send_money.html", {"form": form})
            except OperationalError:
                messages.info(request, f"Transfer operation is not possible now.")
                return render(request, "payapp/send_money.html", {"form": form})

            # Retrieve destination user object
            dst_user = models.User.objects.select_related().get(username=dst_username)

            # Create a record of the transfer
            transfer_record = TransferRecord(
                sender=request.user,
                receiver=dst_user,
                amount=amount_to_transfer,
                timestamp=timezone.now().date()
            )

            transfer_record.save()
            messages.success(request, f"You have sent the request.")

            return redirect("home")
        else:
            return render(request, "payapp/send_money.html", {"form": form})
    else:
        form = BalanceTransferForm()
        return render(request, "payapp/send_money.html", {"form": form})

# Allows users to request from another registered user
def request_payment(request):
    if request.method == 'POST':
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            src_user = request.user
            dst_username = form.cleaned_data["enter_destination_username"]
            amount_to_transfer = form.cleaned_data["enter_amount_to_request"]

            # Check if the user is trying to request money from themselves
            if src_user.username == dst_username:
                messages.error(request, "You cannot request money from yourself.")
                return render(request, "payapp/request_money.html", {"form": form})

            # Get the destination user object
            try:
                dst_user = User.objects.get(username=dst_username)
            except User.DoesNotExist:
                messages.error(request, "You cannot request money from yourself.")
                return render(request, "payapp/request_money.html", {"form": form})

            # Create the payment request
            payment_request = PaymentRequest(
                enter_your_username=src_user,
                enter_destination_username=dst_user,
                amount_to_request=amount_to_transfer
            )

            payment_request.save()
            return redirect("home")
        else:
            # Form is not valid
            print(form.errors)
            return render(request, "payapp/request_money.html", {"form": form})
    else:
        form = PaymentRequestForm()
        return render(request, "payapp/request_money.html", {"form": form})

# Allows the user to accept or deny payment requests
@transaction.atomic
def process_request_payment(request):
    if request.method == 'POST':
        form = RespondToRequestForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            request_id = form.cleaned_data['request_id']

            # Get the payment request object
            payment_request = PaymentRequest.objects.get(id=request_id, enter_destination_username_id=request.user.id)

            src_username = payment_request.enter_your_username
            dst_username = payment_request.enter_destination_username
            amount = payment_request.amount_to_request

            src_balance = Balance.objects.get(name=src_username)
            dst_balance = Balance.objects.get(name=dst_username)

            # If request is accepted and user has sufficient funds, update user's and requester user's balance
            if action == 'accept':
                if src_balance.balance < payment_request.amount_to_request:
                    messages.error(request, "Insufficient funds to accept this request.")
                    return redirect("home")
                try:
                    with (transaction.atomic()):
                        src_balance.balance -= amount
                        dst_balance.balance -= amount
                        src_balance.save()
                        dst_balance.save()
                        payment_request.status = 'accepted'

                        # Create Transfer Record
                        dst_user = models.User.objects.select_related().get(username=dst_username)
                        transfer_record = TransferRecord(
                            sender=dst_user,
                            receiver=request.user,
                            amount=amount,
                            timestamp=timezone.now().date()
                        )
                        transfer_record.save()

                except OperationalError:
                    messages.error(request, "Could not process the request due to a transaction error.")
                    return redirect("home")
            elif action == 'deny':
                payment_request.status = 'denied'
            messages.success(request, f"You have {payment_request.status} the request.")
            payment_request.delete() # Delete the request so that it doesn't display as a notification
            return redirect("home")
        else:
            messages.error(request, "Invalid form data.")
            return redirect("home")
    else:
        messages.error(request, "Invalid action.")
    return render(request, "payapp/home.html")


def view_transactions(request):
    if request.user.is_staff or request.user.is_superuser:
        # If the user is an admin, fetch all transactions
        transactions = list(TransferRecord.objects.all().order_by('-timestamp'))
    else:
        notifications1 = list(TransferRecord.objects.filter(sender=request.user))
        notifications2 = list(TransferRecord.objects.filter(receiver=request.user))
        transactions = notifications1 + notifications2
    return render(request, 'payapp/transactions.html', {'transactions': transactions})


def convert_currency(from_currency, amount):
    headers = {
        'apikey': 'cur_live_0LJH5Am03J0PgB1zVlrEZqRjwXeHKSNKMsCV5rSP'
    }
    amount = float(amount)
    response = requests.request("GET", 'https://api.currencyapi.com/v3/latest', headers=headers)
    if response.status_code == 200:
        data = response.json()
        try:
            rates = {code: details['value'] for code, details in data['data'].items()}
            direct_rate = rates['USD'] / rates[from_currency]
            converted_amount = amount * direct_rate
            return converted_amount

        except Exception as e:
            print(f"An error occurred while fetching currency data: {str(e)}")
            return amount
    else:
        print(f"Failed to fetch currency data: HTTP {response.status_code}")
        return amount


class CurrencyConversion(APIView):

    def get(self, request, currency1, currency2, amount):

        headers = {
            'apikey': 'cur_live_0LJH5Am03J0PgB1zVlrEZqRjwXeHKSNKMsCV5rSP'
        }
        amount = float(amount)

        # GET request to the API to get the currency rates
        response = requests.request("GET", 'https://api.currencyapi.com/v3/latest', headers=headers)

        if response.status_code != 200:
            return Response({'error': 'Failed to fetch currency data'}, status=response.status_code)

        data = response.json()
        # Extract the currency rates from the json and store them in a dictionary
        rates = {code: details['value'] for code, details in data['data'].items()}

        try:
            # Calculate the rate between the currencies and calculate the conversion
            direct_rate = rates[currency2] / rates[currency1]
            converted_amount = amount * direct_rate

            # Return the converted amount and the conversion
            return Response({
                'converted_amount': converted_amount,
                'rate': direct_rate,
            })
        except KeyError as e:
            return Response({'error': f'Invalid currency code: {str(e)}'}, status=404)


def notification_view(request):
    # Filter money requests where the current user is the recipient and the status is 'pending'

    return render(request, 'register/navbar.html')

def home(request):

    context = {}
    if request.user.is_authenticated:
        # Fetch balance for the authenticated user
        try:
            user_balance = Balance.objects.get(name=request.user)
        except Balance.DoesNotExist:
            user_balance = None  # Handle the case where no balance is found

        context['user_balance'] = user_balance.balance if user_balance else 0
        return render(request, 'payapp/home.html', context)

