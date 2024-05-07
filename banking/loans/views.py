from django.shortcuts import render
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import generics
from .models import *
from .serializer import *
from .permissions import IsAdminOrStaffUser,IsCustomerUser
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from django.core.mail import send_mail



class InterestRateCreateAPIView(generics.CreateAPIView):
    queryset = InterestRate.objects.all()
    serializer_class = InterestRateSerializer
    permission_classes = [IsAdminUser]

class InterestRateUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InterestRate.objects.all()
    serializer_class = InterestRateSerializer
    permission_classes = [IsAdminOrStaffUser]

class InterestListAPIView(generics.ListAPIView):
    queryset = InterestRate.objects.all()
    serializer_class = InterestRateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InterestRate.objects.all()



class LoanApplicationCreateAPIView(generics.CreateAPIView):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsCustomerUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.validated_data['user'] = request.user

        loan_type = serializer.validated_data['loan_type']

        amount = Decimal(serializer.validated_data['amount'])
        duration_years = Decimal(serializer.validated_data['duration_months']) / Decimal('12')

        try:
            interest_rate_obj = InterestRate.objects.get(loan_type=loan_type)
            interest_rate = Decimal(interest_rate_obj.rate) / Decimal('100')  # Convert to Decimal and percentage
        except InterestRate.DoesNotExist:
            interest_rate = Decimal('0.10')  # Default interest rate of 10%

        monthly_interest_rate = interest_rate / Decimal('12')

        total_payments = duration_years * Decimal('12')

        # Calculate monthly payment (EMI)
        monthly_payment = (amount * monthly_interest_rate) / (Decimal('1') - (Decimal('1') + monthly_interest_rate) ** -total_payments)

        # Calculate total amount payable after loan term
        total_amount_payable = monthly_payment * total_payments

        # Save the loan application
        self.perform_create(serializer)

        # Retrieve the saved loan application instance
        loan_application = serializer.instance

        return Response({
            "loan_details": {
                "Loan Amount": f"Rs {amount}",
                "Tenure": f"{duration_years} years",
                "Interest Rate": f"{interest_rate * 100}%",
                "Total Amount Payable After Loan Term": f"Rs {total_amount_payable}",
                "Monthly Payment (EMI)": f"Rs {monthly_payment}",
                "Applied Date": loan_application.applied_date.strftime("%Y-%m-%d %H:%M:%S"),
                "Status": loan_application.status,
            },
            "message": "Loan application created successfully."
        }, status=status.HTTP_201_CREATED)

class LoanApplicationListAPIView(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsCustomerUser]

    def get_queryset(self):
        # Retrieve the authenticated user
        user = self.request.user
        # Filter loan applications based on the user
        return LoanApplication.objects.filter(user=user)


class LoanApprovalAPIView(generics.CreateAPIView):
    queryset = LoanApproval.objects.all()
    serializer_class = LoanApprovalSerializer
    permission_classes = [IsAdminOrStaffUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update loan application status
        loan_application = serializer.validated_data['loan_application']
        new_status = serializer.validated_data['new_status']
        loan_application.status = new_status
        loan_application.save()

        # Create loan approval instance
        loan_approval = serializer.save()

        send_mail(
            'Loan Approval Notification',
            f'Your loan application for {loan_application.loan_type} has been {new_status.lower()}.',
            'tkmce.alumniportal@gmail.com',
            [loan_application.user.email],
            fail_silently=True,
        )

        return Response({'message': 'Loan status updated and notification sent'}, status=status.HTTP_201_CREATED)
    
class UserLoanApplicationListView(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAdminOrStaffUser]

    def get_queryset(self):
        # user = self.request.user
        return LoanApplication.objects.all()