from django.urls import path
from .views import *

urlpatterns = [
    path('savings/', CreateAccountAPIView.as_view(), name='account-list'),
    path('deposit/', DepositAPIView.as_view(), name='deposit'),
    path('withdraw/', WithdrawalAPIView.as_view(), name='withdraw'),
    path('transaction/', TransactionHistoryAPIView.as_view(), name='transaction_history'),
    path('admin/transaction/', AllUsersTransactionHistoryAPIView.as_view(), name='all_users_transaction_history'),  # URL for admin/staff view
    path('delete/', DeleteAccountAPIView.as_view(), name='delete_account'),
    path('fixed-deposit/create/', FixedDepositCreateAPIView.as_view(), name='fixed_deposit_create'),
    path('interest-rates/', InterestRateAPIView.as_view(), name='interest-rate-list-create'),
    path('fd/<int:user_id>/', UserFixedDepositsAPIView.as_view(), name='user-fixed-deposits'),
    path('recurrent-deposits/create/', RecurrentDepositCreateAPIView.as_view(), name='recurrent_deposit_create'),
    path('recurrent/<int:user_id>/', UserRecurrentDepositsAPIView.as_view(), name='user-recurrent-deposits'),
    path('fund-transfer/', FundTransferAPIView.as_view(), name='fund_transfer'),
    path('fund-transfers_view/', FundTransferListAPIView.as_view(), name='fund_transfer_list'),
    path('fixed-deposits/', FixedDepositListAPIView.as_view(), name='fixed_deposit_list'),
    path('recurrent-deposits/', RecurrentDepositListAPIView.as_view(), name='recurrent-deposit-list'),
    path('budgets/', BudgetListCreateAPIView.as_view(), name='budget-list-create'),

]
