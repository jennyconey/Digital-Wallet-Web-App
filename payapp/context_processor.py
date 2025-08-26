from django.shortcuts import render
from . import models
from .models import PaymentRequest

# Returns list of user's pending requests to display as their notifications
def request_payment_list(request):
    if request.user.is_authenticated:
        pending_requests = list(PaymentRequest.objects.filter(enter_destination_username=request.user))
        return {"pending_requests": pending_requests}
    return []

