from decimal import Decimal
from datetime import timedelta
from django.db import transaction
from django.utils import timezone

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *

from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')

# ===================== PERMISSIONS =====================
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)


# ===================== ADMIN VIEWS =====================
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class AdminBankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAdminUser]


class AdminLoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def process_loan(self, request, pk=None):
        loan = self.get_object()
        action_type = request.data.get('action')

        if loan.status != 'pending':
            return Response({'error': 'Loan already processed'}, status=400)

        with transaction.atomic():
            if action_type == 'approve':
                loan.status = 'approved'
                loan.approved_by = request.user
                loan.approved_date = timezone.now()
                loan.save()
                self.create_emi_schedule(loan)
            elif action_type == 'reject':
                loan.status = 'rejected'
                loan.approved_by = request.user
                loan.approved_date = timezone.now()
                loan.save()
            else:
                return Response({'error': 'Invalid action'}, status=400)

        return Response({'message': f'Loan {loan.status}', 'status': loan.status})

    def create_emi_schedule(self, loan):
        emi_amount = loan.calculate_emi()
        principal = Decimal(loan.amount)
        monthly_rate = Decimal(loan.interest_rate) / Decimal(1200)
        due_date = timezone.now().date() + timedelta(days=30)

        for i in range(1, loan.duration_months + 1):
            interest = principal * monthly_rate
            principal_payment = emi_amount - interest
            principal -= principal_payment

            EMI.objects.create(
                loan=loan,
                emi_number=i,
                due_date=due_date,
                amount=emi_amount,
                principal=round(principal_payment, 2),
                interest=round(interest, 2),
                status='pending'
            )
            due_date += timedelta(days=30)


class AdminRequestViewSet(viewsets.ModelViewSet):
    queryset = UserRequest.objects.all()
    serializer_class = UserRequestSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def process_request(self, request, pk=None):
        user_request = self.get_object()
        action_type = request.data.get('action')

        with transaction.atomic():
            account = user_request.account

            if action_type == 'approve':
                if user_request.request_type == 'deposit':
                    account.balance += user_request.amount
                    account.save()
                    Transaction.objects.create(
                        account=account,
                        transaction_type='deposit',
                        amount=user_request.amount,
                        description='Deposit request approved'
                    )
                elif user_request.request_type == 'withdrawal':
                    if account.balance < user_request.amount:
                        return Response({'error': 'Insufficient balance'}, status=400)
                    account.balance -= user_request.amount
                    account.save()
                    Transaction.objects.create(
                        account=account,
                        transaction_type='withdrawal',
                        amount=user_request.amount,
                        description='Withdrawal request approved'
                    )
                user_request.status = 'approved'

            elif action_type == 'reject':
                user_request.status = 'rejected'
            elif action_type == 'complete':
                user_request.status = 'completed'
            else:
                return Response({'error': 'Invalid action'}, status=400)

            user_request.processed_by = request.user
            user_request.processed_at = timezone.now()
            user_request.save()

        return Response({'message': 'Request processed', 'status': user_request.status})


# ===================== USER VIEWS =====================
class UserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        accounts = BankAccount.objects.filter(user=user)
        transactions = Transaction.objects.filter(account__in=accounts).order_by('-date')[:10]
        loans = Loan.objects.filter(user=user)
        requests = UserRequest.objects.filter(user=user).order_by('-created_at')[:5]

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            },
            'accounts': BankAccountSerializer(accounts, many=True).data,
            'transactions': TransactionSerializer(transactions, many=True).data,
            'loans': LoanSerializer(loans, many=True).data,
            'requests': UserRequestSerializer(requests, many=True).data
        })


class UserAccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)


class UserTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(account__user=self.request.user)


class UserLoanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)


class UserRequestViewSet(viewsets.ModelViewSet):
    serializer_class = UserRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')


# ===================== PUBLIC =====================
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data.copy()
        data['role'] = 'user'
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
