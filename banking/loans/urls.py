from django.urls import path
from .views import *

urlpatterns = [
    path('loan-interest/', InterestRateCreateAPIView.as_view(), name='create_interest_rate'),
    path('interest/<int:pk>/', InterestRateUpdateDestroyAPIView.as_view(), name='interest-rate-detail'),
    path('loan-applications/', LoanApplicationCreateAPIView.as_view(), name='loan-application-create'),
    path('loans/', InterestListAPIView.as_view(), name='loan_list'),
    path('view-loans/', LoanApplicationListAPIView.as_view(), name='loan-list'),
    path('approve/', LoanApprovalAPIView.as_view(), name='loan-approval'),
    path('user-loan-applications/<int:user_id>/', UserLoanApplicationListView.as_view(), name='user-loan-application-list'),




]
