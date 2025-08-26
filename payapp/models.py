from django.db import models
from django.contrib.auth.models import User


class TransferRecord(models.Model):
    sender = models.ForeignKey(User, related_name='payapp_sent_transactions', related_query_name='payapp_sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='payapp_received_transactions', related_query_name='payapp_receiver', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} sent {self.amount} to {self.receiver.username}"


class Balance(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

def __str__(self):
    details = ''
    details += f'Username     : {self.name}\n'
    details += f'Balance       : {self.balance}\n'
    return details

class PaymentRequest(models.Model):
    enter_your_username = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    enter_destination_username = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    amount_to_request = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('denied', 'Denied')], default='pending')


    def __str__(self):
        return f"{self.enter_your_username} requests {self.enter_destination_username} from {self.amount_to_request} - {self.status}"
