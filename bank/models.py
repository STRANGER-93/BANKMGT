from django.db import models
from django.contrib.auth.models import AbstractUser
import random
from decimal import Decimal

# ===================== USER MODEL =====================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"


# ===================== BANK ACCOUNT MODEL =====================
class BankAccount(models.Model):
    ACCOUNT_TYPES = (
        ('savings', 'Savings'),
        ('current', 'Current'),
    )
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES, default='savings')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)
    
    def generate_account_number(self):
        return f"BNK{random.randint(1000000000, 9999999999)}"
    
    def __str__(self):
        return f"{self.account_number} - {self.user.username}"


# ===================== TRANSACTION MODEL =====================
class Transaction(models.Model):
    TYPE_CHOICES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('loan_disbursement', 'Loan Disbursement'),
    )
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - ₹{self.amount}"


# ===================== LOAN MODEL =====================
class Loan(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('completed', 'Completed'),
    )
    loan_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    duration_months = models.IntegerField(default=12)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.0) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_loans')

    def save(self, *args, **kwargs):
        if not self.loan_id:
            self.loan_id = f"LOAN{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def calculate_emi(self):
        P = float(self.amount)
        R = float(self.interest_rate) / (12 * 100)
        N = self.duration_months
        if R == 0:
            return round(P / N, 2)
        emi = (P * R * (1 + R) ** N) / ((1 + R) ** N - 1)
        return round(emi, 2)
    
    def __str__(self):
        return f"Loan {self.loan_id} - ₹{self.amount}"


# ===================== EMI MODEL =====================
class EMI(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('defaulted', 'Defaulted'),
    )
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    emi_number = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    principal = models.DecimalField(max_digits=10, decimal_places=2)
    interest = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paid_date = models.DateField(null=True, blank=True)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['emi_number']
    
    def __str__(self):
        return f"EMI #{self.emi_number} - ₹{self.amount}"


# ===================== USER REQUEST MODEL =====================
class UserRequest(models.Model):
    REQUEST_TYPES = (
        ('deposit', 'Deposit Money'),
        ('withdrawal', 'Withdraw Money'),
        ('account_issue', 'Account Issue'),
        ('loan_application', 'Loan Application'),
        ('other', 'Other'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    request_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_requests')
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = f"REQ{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.request_id} - {self.request_type}"
