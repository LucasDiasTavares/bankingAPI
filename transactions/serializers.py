from rest_framework import serializers
from rest_framework.exceptions import NotAcceptable
from django.conf import settings
from .models import Transaction, MoneyTransfer
from authentication.models import UserBankAccount
from .constants import DEPOSIT, WITHDRAWAL, TRANSFER_MONEY, TRANSFER_MONEY_RECEIVED


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['id', 'account', 'timestamp', 'amount', 'balance_after_transaction', 'transaction_type',
                  'sender_user_name']


class TransferSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(required=True)

    class Meta:
        model = MoneyTransfer
        fields = '__all__'

    def validate(self, attrs):
        amount_to_be_transferred = attrs.get('amount_to_be_transferred', '')
        destination_account_number = attrs.get('destination_account_number', '')
        user_name = attrs.get('user_name', '')

        # TODO check if my limit is ok, not implemented yet

        current_balance = self.context['current_balance']
        current_username = self.context['current_username']
        balance_after_transaction = self.context['balance_after_transaction']
        current_id = self.context['current_id']
        current_account_number = self.context['current_account_number']

        if user_name != current_username:
            raise NotAcceptable(f"Please check your user name")

        if current_account_number == destination_account_number:
            raise NotAcceptable(f"Please check destination account number: {destination_account_number}")

        if amount_to_be_transferred > current_balance:
            raise NotAcceptable(
                f"You don't have enough money, your current balance is R$ {current_balance}")

        qs = UserBankAccount.objects.filter(account_no=destination_account_number)
        if not qs.exists():
            raise NotAcceptable(f"Wrong destination account number: {destination_account_number}")

        return {
            'amount_to_be_transferred': amount_to_be_transferred,
            'destination_account_number': destination_account_number,
            'user_name': user_name,
            'balance_after_transaction': balance_after_transaction,
            'current_id': current_id,
            'transaction_type': TRANSFER_MONEY
        }

    def create(self, validated_data):
        new_balance = validated_data['balance_after_transaction']
        current_account_instance = UserBankAccount.objects.get(id=validated_data['current_id'])

        destination_account_instance = UserBankAccount.objects.get(
            account_no=validated_data['destination_account_number'])

        destination_user_balance = destination_account_instance.user.balance
        destination_user_balance += validated_data['amount_to_be_transferred']

        transaction_current_user = Transaction.objects.create(
            account=current_account_instance, amount=validated_data['amount_to_be_transferred'],
            balance_after_transaction=validated_data['balance_after_transaction'],
            transaction_type=TRANSFER_MONEY, sender_user_name=destination_account_instance.user.username)

        transaction_destination_user = Transaction.objects.create(
            account=destination_account_instance, amount=validated_data['amount_to_be_transferred'],
            balance_after_transaction=validated_data['balance_after_transaction'],
            transaction_type=TRANSFER_MONEY_RECEIVED, sender_user_name=current_account_instance.user.username)

        money_transfer = MoneyTransfer.objects.create(
            user_name=validated_data['user_name'],
            destination_account_number=validated_data['destination_account_number'],
            amount_to_be_transferred=validated_data['amount_to_be_transferred'])

        destination_update = UserBankAccount.objects.filter(account_no=validated_data['destination_account_number'])
        current_update = UserBankAccount.objects.filter(id=validated_data['current_id'])

        # Update current and destination balance
        current_update.update(balance=new_balance)
        destination_update.update(balance=destination_user_balance)

        validated_data.pop('current_id')
        transaction_current_user.save()
        transaction_destination_user.save()
        money_transfer.save()
        return validated_data


class DepositSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(required=True, decimal_places=2, max_digits=12)

    class Meta:
        model = Transaction
        fields = ['amount']

    def validate(self, attrs):
        amount = attrs.get('amount', '')

        min_deposit_amount = settings.MINIMUM_DEPOSIT_AMOUNT

        if amount < min_deposit_amount:
            raise NotAcceptable(f'You need to deposit at least R$ {min_deposit_amount}')

        # Grabbing the custom context data
        balance_after_transaction = self.context['balance_after_transaction']
        user_account_id = self.context['user_account_id']

        return {
            'account': user_account_id,
            'amount': amount,
            'balance_after_transaction': balance_after_transaction,
            'transaction_type': DEPOSIT,
        }

    def create(self, validated_data):
        new_balance = validated_data['balance_after_transaction']
        account_instance = UserBankAccount.objects.get(id=validated_data['account'])
        validated_data.pop('account')
        transaction = Transaction.objects.create(account=account_instance, **validated_data)
        UserBankAccount.objects.update(balance=new_balance)
        transaction.save()
        return transaction


class WithdrawalSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = Transaction
        fields = ['amount']

    def validate(self, attrs):
        amount = attrs.get('amount', '')

        min_withdrawal_amount = settings.MINIMUM_WITHDRAWAL_AMOUNT
        # Grabbing the custom context data
        maximum_withdrawal = self.context['maximum_withdrawal']
        balance_after_transaction = self.context['balance_after_transaction']
        user_account_id = self.context['user_account_id']
        current_balance = self.context['current_balance']

        if amount < min_withdrawal_amount:
            raise NotAcceptable(f'You need to withdrawal at least R$ {min_withdrawal_amount}')

        if amount > maximum_withdrawal:
            raise NotAcceptable(f'You only can withdrawal a maximum of R$ {maximum_withdrawal}')

        if amount > current_balance:
            raise NotAcceptable(
                f"You don't have enough money, your current balance is R$ {current_balance}")

        return {
            'account': user_account_id,
            'amount': amount,
            'balance_after_transaction': balance_after_transaction,
            'transaction_type': WITHDRAWAL,
        }

    def create(self, validated_data):
        new_balance = validated_data['balance_after_transaction']
        account_instance = UserBankAccount.objects.get(id=validated_data['account'])
        validated_data.pop('account')
        transaction = Transaction.objects.create(account=account_instance, **validated_data)
        UserBankAccount.objects.update(balance=new_balance)
        transaction.save()
        return transaction
