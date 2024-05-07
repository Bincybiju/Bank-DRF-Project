from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import  Savings
from .serializer import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404
from .permissions import IsAdminOrStaffUser,IsCustomerUser
from datetime import datetime,timedelta,date

class CreateAccountAPIView(APIView):
    permission_classes = [IsCustomerUser]

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
            account = serializer.save()
            account_number = account.account_number
            message = f"Account created successfully. Your account number is: {account_number}"
            return Response({"message": message}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
            user_accounts = Savings.objects.filter(user=request.user)
            serializer = AccountSerializer(user_accounts, many=True)
            return Response(serializer.data)

class DeleteAccountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        account_number = request.data.get('account_number')
        if not account_number:
            return Response({'error': 'Account number is required'}, status=status.HTTP_400_BAD_REQUEST)

        account = get_object_or_404(Savings, account_number=account_number)
        if account.balance == 0:
            account.delete()
            return Response({'message': 'Account deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Cannot delete account with non-zero balance'}, status=status.HTTP_400_BAD_REQUEST)
   
class DepositAPIView(generics.GenericAPIView):
    serializer_class = DepositSerializer
    permission_classes = [IsCustomerUser]

    def post(self, request):
        account_number = request.data.get('account_number')
        amount = request.data.get('amount')
        description = request.data.get('description', '')  # Get the description from the request data

        if not account_number or not amount:
            return Response({'error': 'Both account_number and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

        savings_account = get_object_or_404(Savings, account_number=account_number, user=request.user)
        serializer = self.get_serializer(data={'amount': amount, 'description': description})  # Pass description to serializer

        if serializer.is_valid():
            amount = serializer.validated_data.get('amount')
            description = serializer.validated_data.get('description', '')  # Get validated description
            try:
                savings_account.deposit(amount, description)  # Pass description to deposit method
                new_balance = savings_account.balance
                return Response({'message': 'Deposit successful', 'new_balance': new_balance}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class WithdrawalAPIView(generics.GenericAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsCustomerUser]
    def post(self, request):
        account_number = request.data.get('account_number')
        amount = request.data.get('amount')
        description = request.data.get('description', '')

        if not account_number or not amount:
            return Response({'error': 'Both account_number and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

        savings_account = get_object_or_404(Savings, account_number=account_number, user=request.user)
        serializer = self.get_serializer(data={'amount': amount})

        if serializer.is_valid():
            amount = serializer.validated_data.get('amount')
            if amount > savings_account.balance:
                return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

            category_name = description  
            budget_control = BudgetControl.objects.filter(account_number=account_number, category_name=category_name).first()
            if budget_control:
                if amount > budget_control.balance_budget:
                    subject = "Budget Alert: High Expenses"
                    message = f"Dear user,\n\nYou made a withdrawal of ${amount} from account number {account_number} for the category '{category_name}', which exceeds the balance budget.\n\nCategory: {category_name}\nWithdrawal Amount: ${amount}\nAccount Number: {account_number}\nTransaction Date: {timezone.now()}\n\nPlease review your budget and adjust accordingly.\n\nBest regards,\nYour Budget App Team"
                    from_email = "your_budget_app@example.com"  
                    to_email = [request.user.email]  
                    send_mail(subject, message, from_email, to_email)

                budget_control.balance_budget -= amount
                budget_control.save()

            try:
                savings_account.withdraw(amount, description)
                new_balance = savings_account.balance
                return Response({'message': 'Withdrawal successful', 'new_balance': new_balance}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TransactionHistoryAPIView(APIView):
    permission_classes = [IsCustomerUser]

    def post(self, request):
        account_number = request.data.get('account_number')

        if not account_number:
            return Response({'error': 'Account number is required'}, status=status.HTTP_400_BAD_REQUEST)

        account = get_object_or_404(Savings, account_number=account_number, user=request.user)
        savings_transactions = SavingsTransaction.objects.filter(account=account)
        current_transactions = CurrentTransaction.objects.filter(account=account)

        response_data = {}

        if savings_transactions.exists():
            savings_data = [{'transaction_type': transaction.transaction_type, 'amount': transaction.amount, 'date': transaction.date} for transaction in savings_transactions]
            response_data['savings_transactions'] = savings_data

        if current_transactions.exists():
            current_data = [{'transaction_type': transaction.transaction_type, 'amount': transaction.amount, 'date': transaction.date} for transaction in current_transactions]
            response_data['current_transactions'] = current_data

        if not response_data:
            return Response({'error': 'No transactions found for the provided account number'}, status=status.HTTP_404_NOT_FOUND)

        return Response(response_data)

class AllUsersTransactionHistoryAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        account_number = request.data.get('account_number')

        if not account_number:
            return Response({'error': 'Account number is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch all accounts with the provided account number
        savings_accounts = Savings.objects.filter(account_number=account_number)
        current_accounts = Savings.objects.filter(account_number=account_number)

        if not (savings_accounts.exists() or current_accounts.exists()):
            return Response({'error': 'No accounts found with the provided account number'}, status=status.HTTP_404_NOT_FOUND)

        response_data = []

        # Retrieve transaction history for each account
        for account in savings_accounts:
            savings_transactions = SavingsTransaction.objects.filter(account=account)
            if savings_transactions.exists():
                savings_data = [{'transaction_type': transaction.transaction_type, 'amount': transaction.amount, 'date': transaction.date} for transaction in savings_transactions]
                response_data.append({'account_number': account.account_number, 'account_type': 'SAVINGS', 'transactions': savings_data})

        for account in current_accounts:
            current_transactions = CurrentTransaction.objects.filter(account=account)
            if current_transactions.exists():
                current_data = [{'transaction_type': transaction.transaction_type, 'amount': transaction.amount, 'date': transaction.date} for transaction in current_transactions]
                response_data.append({'account_number': account.account_number, 'account_type': 'CURRENT', 'transactions': current_data})

        if not response_data:
            return Response({'error': 'No transactions found for the provided account number'}, status=status.HTTP_404_NOT_FOUND)

        return Response(response_data)

class InterestRateAPIView(APIView):
    serializer_class=InterestRateSerializer
    permission_classes = [IsAdminOrStaffUser]

    def get(self, request):
        try:
            interest_rate = InterestRate.objects.get(id=1)  # Assuming only one interest rate will be stored with ID 1
            serializer = InterestRateSerializer(interest_rate)
            return Response(serializer.data)
        except InterestRate.DoesNotExist:
            return Response({"error": "No interest rate found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            interest_rate = InterestRate.objects.get(id=1)
            serializer = InterestRateSerializer(interest_rate, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except InterestRate.DoesNotExist:
            serializer = InterestRateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(id=1)  # Set ID to 1 to ensure only one interest rate exists
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FixedDepositCreateAPIView(generics.CreateAPIView):
    queryset = FixedDeposit.objects.all()
    serializer_class = FixedDepositSerializer
    permission_classes = [IsCustomerUser]

    def calculate_total_amount(self, amount, interest_rate, duration_months):
        # Convert duration from months to days
        duration_days = duration_months * 30

        # Calculate total amount after the fixed deposit duration
        total_amount = amount * (1 + Decimal(interest_rate.rate) / 100) ** (duration_days / Decimal(365))
        return total_amount
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated data from serializer
        amount = serializer.validated_data['amount']
        duration_months = serializer.validated_data['duration_months']
        start_date = timezone.now().date()

        # Calculate end date based on duration in months
        end_date = start_date + timedelta(days=duration_months * 30)

        # Fetch interest rate (assuming InterestRate model exists and has a 'rate' field)
        interest_rate = InterestRate.objects.first()

        # Calculate total amount
        total_amount = self.calculate_total_amount(amount, interest_rate, duration_months)

        # Save the fixed deposit
        serializer.save(user=request.user, end_date=end_date, total_amount=total_amount)

        # Construct response data
        response_data = serializer.data
        response_data['end_date'] = end_date
        response_data['total_amount'] = total_amount

        # Return response with serializer data
        return Response(response_data, status=status.HTTP_201_CREATED)
    
class FixedDepositListAPIView(generics.ListAPIView):
    queryset = FixedDeposit.objects.all()
    serializer_class = FixedDepositSerializer
    permission_classes = [IsCustomerUser]

    def get_queryset(self):
        # Filter the queryset to include only fixed deposits of the current user
        user = self.request.user
        return FixedDeposit.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        # Get the queryset filtered by the current user
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({"message": "No fixed deposits found for the current user."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the queryset
        serializer = self.get_serializer(queryset, many=True)
        
        # Return the serialized data as a response
        return Response(serializer.data)
  
    
class UserFixedDepositsAPIView(generics.ListAPIView):
    serializer_class = FixedDepositSerializer
    permission_classes = [IsAdminOrStaffUser]
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user_fixed_deposits = FixedDeposit.objects.filter(user_id=user_id)
        return user_fixed_deposits  
    
   
from decimal import Decimal
class RecurrentDepositCreateAPIView(generics.CreateAPIView):
    queryset = RecurrentDeposit.objects.all()
    serializer_class = RecurrentDepositSerializer
    permission_classes = [IsCustomerUser]

    def calculate_total_amount(self, amount, interest_rate, duration_days):
        total_amount = amount * (1 + Decimal(interest_rate.rate) / 100) ** (duration_days / Decimal(365))
        return total_amount

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated data from serializer
        amount = serializer.validated_data['amount']
        frequency = serializer.validated_data['frequency']
        start_date = timezone.now().date()
        if frequency == 'MONTHLY':
            end_date = start_date + timedelta(days=30)
        elif frequency == 'QUARTERLY':
            end_date = start_date + timedelta(days=90)
        elif frequency == 'HALF_YEARLY':
            end_date = start_date + timedelta(days=182)
        elif frequency == 'YEARLY':
            end_date = start_date + timedelta(days=365)
        else:
            return Response({"error": "Invalid frequency"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate duration in days
        duration_days = (end_date - start_date).days

        # Fetch interest rate (assuming InterestRate model exists and has a 'rate' field)
        interest_rate = InterestRate.objects.first()

        if not interest_rate:
            return Response({"error": "No interest rate found"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total amount
        total_amount = self.calculate_total_amount(amount, interest_rate, duration_days)

        # Save recurrent deposit
        serializer.save(user=request.user, end_date=end_date, total_amount=total_amount)

        # Construct response data
        response_data = serializer.data
        response_data['total_amount_after_duration'] = total_amount
        response_data['end_date'] = end_date

        return Response(response_data, status=status.HTTP_201_CREATED)

class RecurrentDepositListAPIView(generics.ListAPIView):
    queryset = FixedDeposit.objects.all()
    serializer_class = RecurrentDepositSerializer
    permission_classes = [IsCustomerUser]


    def get_queryset(self):
        # Filter the queryset to include only fixed deposits of the current user
        user = self.request.user
        return RecurrentDeposit.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        # Get the queryset filtered by the current user
        queryset = self.get_queryset()
        
        if not queryset.exists():
            return Response({"message": "No fixed deposits found for the current user."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the queryset
        serializer = self.get_serializer(queryset, many=True)
        
        # Return the serialized data as a response
        return Response(serializer.data)



class UserRecurrentDepositsAPIView(generics.ListAPIView):
    serializer_class = RecurrentDepositSerializer
    permission_classes = [IsAdminOrStaffUser]
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user_recurrent_deposits = RecurrentDeposit.objects.filter(user_id=user_id)
        return user_recurrent_deposits  
    
class FundTransferAPIView(APIView):
    permission_classes = [IsCustomerUser]

    def post(self, request):
        serializer = FundTransferSerializer(data=request.data)
        if serializer.is_valid():
            receiver_account_number = serializer.validated_data['receiver_account_number']
            amount = serializer.validated_data['amount']
            
            sender_accounts = request.user.savings_set.all()
            if not sender_accounts.exists():
                return Response({"error": "Sender account not found"}, status=status.HTTP_404_NOT_FOUND)

            sender_account_number = serializer.validated_data['sender_account_number']
            try:
                sender_account = sender_accounts.get(account_number=sender_account_number)
            except Savings.DoesNotExist:
                return Response({"error": "Sender account not found"}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                receiver_account = Savings.objects.get(account_number=receiver_account_number)
            except Savings.DoesNotExist:
                return Response({"error": "Receiver account not found"}, status=status.HTTP_404_NOT_FOUND)
            
            if sender_account.balance < amount:
                return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
            
            sender_account.balance -= amount
            receiver_account.balance += amount
            sender_account.save()
            receiver_account.save()
            
            serializer.save(sender_account_number=sender_account.account_number)
            
            new_balance = sender_account.balance
            response_data = serializer.data
            response_data['new_sender_balance'] = new_balance
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        user_accounts = request.user.savings_set.values_list('account_number', 'account_type')
        
        fund_transfers = FundTransfer.objects.filter(sender_account_number__in=[account[0] for account in user_accounts])

        serializer = FundTransferSerializer(fund_transfers, many=True)
        
        response_data = serializer.data
        for idx, transfer in enumerate(response_data):
            response_data[idx]['sender_account_type'] = dict(user_accounts).get(transfer['sender_account_number'], None)
        
        return Response(response_data)

class FundTransferListAPIView(generics.ListAPIView):
    queryset = FundTransfer.objects.all()
    serializer_class = FundTransferSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class BudgetListCreateAPIView(APIView):
    permission_classes = [IsCustomerUser]

    def get(self, request):
        budgets = BudgetControl.objects.all()
        serializer = BudgetSerializer(budgets, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BudgetSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    