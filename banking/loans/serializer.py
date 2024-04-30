from rest_framework import serializers
from .models import LoanApplication, LoanApproval,InterestRate

class InterestRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestRate
        fields = '__all__'
        
class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ['loan_type', 'amount', 'duration_months', 'status', 'applied_date']
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be greater than zero.")
        elif value < 5000:
            raise serializers.ValidationError("Loan amount must be at least 5000.")
        return value

    def validate_duration_months(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan duration must be greater than zero.")
        return value

class LoanApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApproval
        fields = ['loan_application', 'interest_rate']
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.core.mail import send_mail

class LoanApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApproval
        fields = ['loan_application', 'new_status']