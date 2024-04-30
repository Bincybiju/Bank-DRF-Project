from rest_framework import serializers
from .models import *

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Savings
        fields = ['id', 'balance', 'account_type']

class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)  # Description field added to the serializer

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

class WithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)  # Add a description field


    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    def validate(self, data):
        amount = data.get('amount')
        category_name = data.get('category_name')
        account_number = self.context['request'].data.get('account_number')
        savings_account = Savings.objects.get(account_number=account_number)

        if amount > savings_account.balance:
            raise serializers.ValidationError("Insufficient funds.")

        if amount > savings_account.balance_budget:
            # Send email notification
            subject = "Budget Alert: High Expenses"
            message = f"Dear user,\n\nYou made a withdrawal of ${amount} from account number {account_number} for the category '{category_name}', which exceeds the balance budget.\n\nCategory: {category_name}\nWithdrawal Amount: ${amount}\nAccount Number: {account_number}\nTransaction Date: {timezone.now()}\n\nPlease review your budget and adjust accordingly.\n\nBest regards,\nYour Budget App Team"
            from_email = "your_budget_app@example.com"  # Replace with your sender email
            to_email = [self.context['request'].user.email]  # Assuming user is authenticated and has an email field
            send_mail(subject, message, from_email, to_email)

        return data


class SavingsTransactionSerializer(serializers.ModelSerializer):
    account_id = serializers.PrimaryKeyRelatedField(source='account', read_only=True)

    class Meta:
        model = SavingsTransaction
        fields = ['account_id', 'transaction_type', 'amount', 'date']

class CurrentTransactionSerializer(serializers.ModelSerializer):
    account_id = serializers.PrimaryKeyRelatedField(source='account', read_only=True)

    class Meta:
        model = CurrentTransaction
        fields = ['account_id', 'transaction_type', 'amount', 'date']

class InterestRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestRate
        fields = ['id', 'rate']

class FixedDepositSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    end_date = serializers.DateField(read_only=True)

    class Meta:
        model = FixedDeposit
        fields = ['id', 'amount', 'duration_months', 'total_amount', 'end_date']

    def validate_amount(self, value):
        if value < 5000:
            raise serializers.ValidationError("Amount must be greater than 5000.")
        return value

    def validate_duration_months(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be a positive integer.")
        return value
    
    
class RecurrentDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurrentDeposit
        fields = ['id',  'amount', 'frequency', 'created_at', 'total_amount', 'end_date']
    
    def validate_amount(self, value):
        if value < 500:
            raise serializers.ValidationError("Amount must be greater than 500.")
        return value
    
    

class FundTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundTransfer
        fields = ['sender_account_number', 'receiver_account_number', 'amount', 'timestamp']



    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number")
        return value
    def get_account_type(self, obj):
        # Retrieve the account type of the sender's account
        try:
            sender_account = Savings.objects.get(account_number=obj.sender_account_number)
            return sender_account.account_type
        except Savings.DoesNotExist:
            return None
from django.core.mail import send_mail
from rest_framework import viewsets

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetControl
        fields = ['id', 'category_name', 'account_number', 'alloted_budget', 'balance_budget', 'start_date', 'end_date']