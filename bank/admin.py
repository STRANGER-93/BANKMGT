from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

# ===================== USER ADMIN =====================
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'address')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email', 'phone')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)


# ===================== BANK ACCOUNT ADMIN =====================
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'account_type', 'balance', 'status', 'created_at')
    list_filter = ('account_type', 'status')
    search_fields = ('account_number', 'user__username', 'user__email')
    readonly_fields = ('account_number', 'created_at')


# ===================== TRANSACTION ADMIN =====================
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'date')
    list_filter = ('transaction_type',)
    search_fields = ('account__account_number', 'account__user__username')


# ===================== LOAN ADMIN =====================
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'user', 'amount', 'duration_months', 'interest_rate', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('loan_id', 'user__username', 'user__email')
    readonly_fields = ('loan_id', 'created_at', 'approved_date', 'approved_by')


# ===================== EMI ADMIN =====================
class EMIAdmin(admin.ModelAdmin):
    list_display = ('loan', 'emi_number', 'due_date', 'amount', 'principal', 'interest', 'status', 'paid_date')
    list_filter = ('status',)
    search_fields = ('loan__loan_id', 'loan__user__username')


# ===================== USER REQUEST ADMIN =====================
class UserRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'user', 'request_type', 'status', 'account', 'amount', 'created_at', 'processed_at', 'processed_by')
    list_filter = ('request_type', 'status')
    search_fields = ('request_id', 'user__username', 'account__account_number')
    readonly_fields = ('request_id', 'created_at', 'processed_at', 'processed_by')


# ===================== REGISTER MODELS =====================
admin.site.register(User, UserAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(EMI, EMIAdmin)
admin.site.register(UserRequest, UserRequestAdmin)
