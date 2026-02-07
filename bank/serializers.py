from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, BankAccount, Transaction, Loan, EMI, UserRequest

# ===================== USER SERIALIZER =====================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])  # 🔑 hash password
        user.save()
        return user


# ===================== BANK ACCOUNT SERIALIZER =====================
class BankAccountSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = BankAccount
        fields = ['id', 'account_number', 'user', 'user_name', 'account_type', 'balance', 'status']
        read_only_fields = ['account_number']


# ===================== TRANSACTION SERIALIZER =====================
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'transaction_type', 'amount', 'date']
        read_only_fields = ['date']


# ===================== LOAN SERIALIZER =====================
class LoanSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    emi_amount = serializers.SerializerMethodField()
    total_payable = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = [
            'id', 'loan_id', 'user', 'user_name', 'amount', 'duration_months',
            'interest_rate', 'status', 'emi_amount', 'total_payable',
            'created_at', 'approved_date', 'approved_by'
        ]
        read_only_fields = ['loan_id', 'created_at', 'approved_date', 'approved_by']
    
    def get_emi_amount(self, obj):
        return obj.calculate_emi()
    
    def get_total_payable(self, obj):
        emi = obj.calculate_emi()
        return round(emi * obj.duration_months, 2)


# ===================== EMI SERIALIZER =====================
class EMISerializer(serializers.ModelSerializer):
    loan_id = serializers.CharField(source='loan.loan_id', read_only=True)
    
    class Meta:
        model = EMI
        fields = '__all__'


# ===================== USER REQUEST SERIALIZER =====================
class UserRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    account_number = serializers.CharField(source='account.account_number', read_only=True, allow_null=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    
    class Meta:
        model = UserRequest
        fields = [
            'id', 'request_id', 'user', 'user_name', 'request_type',
            'request_type_display', 'account', 'account_number', 'amount',
            'description', 'status', 'admin_note', 'created_at', 'processed_at'
        ]
        read_only_fields = ['request_id', 'created_at', 'processed_at', 'processed_by']
