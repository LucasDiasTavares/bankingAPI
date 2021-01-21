from django.urls import path
from .views import (TransactionReportListAPIView,
                    TransactionReportTodayListAPIView,
                    TransactionReportDaysAgoListAPIView,
                    DepositCreateAPIView,
                    WithdrawalCreateAPIView,
                    TransferCreateAPIView)

app_name = 'transactions'

urlpatterns = [
    path("deposit/", DepositCreateAPIView.as_view(), name="deposit"),
    path("report/", TransactionReportListAPIView.as_view(), name="report"),
    path("report/today/", TransactionReportTodayListAPIView.as_view(), name="report-today"),
    path("report/<int:days>/", TransactionReportDaysAgoListAPIView.as_view(), name="report-day-ago"),
    path("withdrawal/", WithdrawalCreateAPIView.as_view(), name="withdrawal"),
    path("transfer/", TransferCreateAPIView.as_view(), name="money-transfer"),
]
