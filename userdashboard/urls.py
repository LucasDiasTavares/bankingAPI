from .views import ExpensesCategorySumary, ExpensesComingSumary, IncomeSourceSumary
from django.urls import path


urlpatterns = [
    path('expenses-category-sumary/<int:days>/', ExpensesCategorySumary.as_view(), name="expenses-category-sumary"),
    path('expenses-coming-sumary/<int:days>/', ExpensesComingSumary.as_view(), name="expenses-coming-sumary"),
    path('incomes-source-sumary/<int:days>/', IncomeSourceSumary.as_view(), name="incomes-source-sumary"),
]
