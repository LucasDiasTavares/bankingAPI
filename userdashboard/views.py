from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import response, status
from rest_framework import permissions
from expenses.models import Expense
from expenses.serializers import ExpenseSerializer
from incomes.models import Income
import datetime


class ExpensesCategorySumary(APIView):

    def get_category_amount(self, expense_list, category):
        expenses = expense_list.filter(category=category)
        amount = 0

        for expense in expenses:
            amount += expense.amount

        return {'amount': str(amount)}

    def get_category(self, expense):
        return expense.category

    def get(self, request, days):
        today_date = datetime.date.today()
        date_ago = today_date-datetime.timedelta(days)
        expenses = Expense.objects.filter(
            owner=request.user, date__gte=date_ago, date__lte=today_date)

        result = {}

        categories = list(set(map(self.get_category, expenses)))

        for expense in expenses:
            for category in categories:
                result[category] = self.get_category_amount(expenses, category)

        return response.Response({'category_data_total_amount_ago': result}, status=status.HTTP_200_OK)


class ExpensesComingSumary(ListAPIView):
    serializer_class = ExpenseSerializer
    queryset = Expense.objects.all()
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        today_date = datetime.date.today()
        coming_date = today_date + datetime.timedelta(self.kwargs['days'])
        queryset = Expense.objects.filter(owner=self.request.user, date__gte=today_date, date__lte=coming_date)
        return queryset


class IncomeSourceSumary(APIView):

    def get_source_amount(self, income_list, source):
        incomes = income_list.filter(source=source)
        amount = 0

        for income in incomes:
            amount += income.amount

        return {'amount': str(amount)}

    def get_source(self, income, days):
        return income.source

    def get(self, request, days):
        today_date = datetime.date.today()
        year_ago = today_date-datetime.timedelta(days=days)
        incomes = Income.objects.filter(
            owner=request.user, date__gte=year_ago, date__lte=today_date)

        result = {}

        sources = list(set(map(self.get_source, incomes)))

        for income in incomes:
            for source in sources:
                result[source] = self.get_source_amount(incomes, source)

        return response.Response({'income_data_total_amount_ago': result}, status=status.HTTP_200_OK)
