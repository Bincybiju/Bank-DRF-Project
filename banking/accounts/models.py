# models.py
import random
import string
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.dateformat import DateFormat

class Savings(models.Model):
    SAVINGS = 'SAVINGS'
    CURRENT = 'CURRENT'

    ACCOUNT_TYPES = [
        (SAVINGS, 'Savings'),
        (CURRENT, 'Current'),
    ]

    SAVINGS_TRANSACTION_LIMIT = 200000  

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    account_number = models.CharField(max_length=10, unique=True, default=0)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)

    def generate_account_number(self):
        return ''.join(random.choices(string.digits, k=10))
    
    def deposit(self, amount, description=None):  
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if self.account_type == self.SAVINGS and amount > self.SAVINGS_TRANSACTION_LIMIT:
            raise ValueError("Deposit amount exceeds maximum transaction limit for savings accounts")
        self.balance += amount
        self.save()
        
        if self.account_type == self.SAVINGS: 
            SavingsTransaction.objects.create(
                account=self,
                transaction_type='DEPOSIT',
                amount=amount,
                description=description, 
                date=timezone.now()
            )
        elif self.account_type == self.CURRENT:  
            CurrentTransaction.objects.create(
                account=self,
                transaction_type='DEPOSIT',
                amount=amount,
                description=description,  
                date=timezone.now()
            )
  
    def withdraw(self, amount, description=None):  
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        if self.account_type == self.SAVINGS and amount > self.SAVINGS_TRANSACTION_LIMIT:
            raise ValueError("Withdrawal amount exceeds maximum transaction limit for savings accounts")
        self.balance -= amount
        self.save()
        if description:
            try:
                savings_goal = SavingsGoal.objects.get(account_number=self.account_number, description=description)
                savings_goal.current_progress += amount
                savings_goal.save()
            except SavingsGoal.DoesNotExist:
                pass  
        
        if self.account_type == self.SAVINGS:  
            SavingsTransaction.objects.create(
                account=self,
                transaction_type='WITHDRAWAL',
                amount=amount,
                description=description, 
                date=timezone.now()
            )
        elif self.account_type == self.CURRENT:  
            CurrentTransaction.objects.create(
                account=self,
                transaction_type='WITHDRAWAL',
                amount=amount,
                description=description,  
                date=timezone.now()
            )

class SavingsTransaction(models.Model):
    DEPOSIT = 'DEPOSIT'
    WITHDRAWAL = 'WITHDRAWAL'

    TRANSACTION_TYPES = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal'),
    ]
    account = models.ForeignKey(Savings, on_delete=models.CASCADE, related_name='saving_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True) 


    def __str__(self):
        return f"{self.transaction_type} of {self.amount} on {self.date}"
    
class CurrentTransaction(models.Model):
    DEPOSIT = 'DEPOSIT'
    WITHDRAWAL = 'WITHDRAWAL'

    TRANSACTION_TYPES = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal'),
    ]
    account = models.ForeignKey(Savings, on_delete=models.CASCADE, related_name='current_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True) 


    def __str__(self):
        return f"{self.transaction_type} of {self.amount} on {self.date}"
    
class InterestRate(models.Model):
    rate = models.DecimalField(max_digits=5, decimal_places=2)

class FixedDeposit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    duration_months = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Fixed Deposit of {self.amount} for {self.user.username}"

    
FREQUENCY_CHOICES = [
    ('MONTHLY', 'Monthly'),
    ('QUARTERLY', 'Quarterly'),
    ('HALF_YEARLY', 'Half-Yearly'),
    ('YEARLY', 'Yearly'),
]

class RecurrentDeposit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Recurrent Deposit of {self.amount} for {self.user.username}"
    
class FundTransfer(models.Model):
    sender_account_number = models.CharField(max_length=10)
    receiver_account_number = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

class BudgetControl(models.Model):
    category_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=10)     
    alloted_budget = models.DecimalField(max_digits=10, decimal_places=2)
    balance_budget = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.account_number} - {self.expense_category.category_name} - {self.start_date} to {self.end_date}"

class SavingsGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=10)  # Account number associated with the savings goal
    description = models.CharField(max_length=255)  # Description for which the savings goal is set
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_progress = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    achieved = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()

   