from django.db import models
from authentication.models import UserBankAccount
from .constants import TRANSACTION_TYPE_CHOICES


class Transaction(models.Model):
    account = models.ForeignKey(
        to=UserBankAccount,
        related_name='transaction',
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    balance_after_transaction = models.DecimalField(
        decimal_places=2,
        max_digits=12
    )
    transaction_type = models.PositiveSmallIntegerField(
        choices=TRANSACTION_TYPE_CHOICES
    )
    sender_user_name = models.CharField(max_length=100, null=True, blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.account.account_no} - {self.account.account_type} - {self.transaction_type} - R$ {self.amount}'

    class Meta:
        ordering = ['-timestamp']


class MoneyTransfer(models.Model):
    user_name = models.CharField(max_length=150, default=None)
    destination_account_number = models.IntegerField()
    amount_to_be_transferred = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
