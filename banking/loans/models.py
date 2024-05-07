from django.db import models
from django.conf import settings  # Import the settings module

class InterestRate(models.Model):
    LOAN_TYPES = [
        ('Personal Loan', 'Personal Loan'),
        ('Home Loan', 'Home Loan'),
        ('Car Loan', 'Car Loan'),
        ('Education Loan', 'Education Loan'),
        # Add more loan types as needed
    ]

    loan_type = models.CharField(max_length=100, choices=LOAN_TYPES, unique=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # Interest rate in percentage

    def __str__(self):
        return f"{self.loan_type} Interest Rate: {self.rate}%"

class LoanApplication(models.Model):
    LOAN_TYPES = [
        ('Personal Loan', 'Personal Loan'),
        ('Home Loan', 'Home Loan'),
        ('Car Loan', 'Car Loan'),
        ('Education Loan', 'Education Loan'),
        # Add more loan types as needed
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loan_applications')
    loan_type = models.CharField(max_length=100, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    duration_months = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.loan_type} Application"
    
class LoanApproval(models.Model):
    loan_application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE)
    approved_date = models.DateField(auto_now_add=True)
    new_status = models.CharField(max_length=20, choices=LoanApplication.STATUS_CHOICES)

    def __str__(self):
        return f"{self.loan_application.user.username} - {self.loan_application.loan_type} Approval"