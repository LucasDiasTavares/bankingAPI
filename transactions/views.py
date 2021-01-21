from decimal import Decimal
from rest_framework import generics, status
from rest_framework import permissions
from rest_framework.response import Response
from .models import Transaction
from .renderers import CustomRender
from .serializers import (
    TransactionSerializer,
    DepositSerializer,
    TransferSerializer,
    WithdrawalSerializer)
from django.utils import timezone
import datetime
from utils.custompagination import MaxSizePerPage30, MaxSizePerPage10


class TransactionReportDaysAgoListAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MaxSizePerPage10

    def get_queryset(self, **kwargs):
        today = timezone.now()
        date_ago = today - datetime.timedelta(self.kwargs['days'])

        return self.queryset.filter(account=self.request.user.account, timestamp__gte=date_ago)


class TransactionReportTodayListAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MaxSizePerPage30

    def get_queryset(self):
        return self.queryset.filter(account=self.request.user.account, timestamp__day=timezone.now().day)


class TransactionReportListAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = MaxSizePerPage30

    def get_queryset(self):
        return self.queryset.filter(account=self.request.user.account)


class TransferCreateAPIView(generics.GenericAPIView):
    serializer_class = TransferSerializer
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (CustomRender,)

    def post(self, request):
        transfer = request.data
        serializer = self.serializer_class(data=transfer)

        # sending data to serializer throw context
        balance_after_transaction = self.request.user.account.balance
        balance_after_transaction -= Decimal(transfer['amount_to_be_transferred'])
        serializer.context['balance_after_transaction'] = balance_after_transaction
        current_balance = self.request.user.account.balance
        serializer.context['current_balance'] = current_balance
        current_username = self.request.user.username
        serializer.context['current_username'] = current_username
        current_id = self.request.user.account.id
        serializer.context['current_id'] = current_id
        current_account_number = self.request.user.account.account_no
        serializer.context['current_account_number'] = current_account_number

        serializer.is_valid(raise_exception=True)
        transfer_data = serializer.save()

        balance_before_transaction = transfer_data['balance_after_transaction'] + transfer_data[
            'amount_to_be_transferred']

        return Response(
            {'username': transfer_data['user_name'],
             'balance_before_transaction': balance_before_transaction,
             'amount': transfer_data['amount_to_be_transferred'],
             'balance_after_transaction': transfer_data['balance_after_transaction'],
             'destination_account_number': transfer_data['destination_account_number'],
             'transaction_type': transfer_data['transaction_type']}, status=status.HTTP_201_CREATED)


class DepositCreateAPIView(generics.GenericAPIView):
    serializer_class = DepositSerializer
    queryset = Transaction.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (CustomRender,)

    def post(self, request):
        deposit = request.data
        serializer = self.serializer_class(data=deposit)

        # Adding custom data to my context serializer
        balance_after_transaction = self.request.user.account.balance
        balance_after_transaction += Decimal(deposit['amount'])
        serializer.context['balance_after_transaction'] = balance_after_transaction
        user_account_id = self.request.user.account.id
        serializer.context['user_account_id'] = user_account_id

        serializer.is_valid(raise_exception=True)
        deposit_data = serializer.save()
        balance_before_transaction = deposit_data.balance_after_transaction - deposit_data.amount

        return Response(
            {'account_id': deposit_data.account.id,
             'balance_before_transaction': balance_before_transaction,
             'amount': deposit_data.amount,
             'balance_after_transaction': deposit_data.balance_after_transaction,
             'transaction_type': deposit_data.transaction_type}, status=status.HTTP_201_CREATED)


class WithdrawalCreateAPIView(generics.GenericAPIView):
    serializer_class = WithdrawalSerializer
    queryset = Transaction.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (CustomRender,)

    def post(self, request):
        withdrawal = request.data
        serializer = self.serializer_class(data=withdrawal)

        balance_after_transaction = self.request.user.account.balance
        balance_after_transaction -= Decimal(withdrawal['amount'])
        user_account_id = self.request.user.account.id
        serializer.context['user_account_id'] = user_account_id
        current_balance = self.request.user.account.balance
        serializer.context['current_balance'] = current_balance

        # Adding custom data to my context serializer
        serializer.context['balance_after_transaction'] = balance_after_transaction
        serializer.context['maximum_withdrawal'] = self.request.user.account.account_type.maximum_withdrawal_amount

        serializer.is_valid(raise_exception=True)
        withdrawal_data = serializer.save()
        balance_before_transaction = withdrawal_data.balance_after_transaction + withdrawal_data.amount
        balance_before_transaction = float(balance_before_transaction)
        balance_after_transaction = float(withdrawal_data.balance_after_transaction)

        return Response(
            {'account_id': withdrawal_data.account.id,
             'balance_before_transaction': balance_before_transaction,
             'amount': withdrawal_data.amount,
             'balance_after_transaction': balance_after_transaction,
             'transaction_type': withdrawal_data.transaction_type}, status=status.HTTP_201_CREATED)
