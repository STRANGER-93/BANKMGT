from decimal import Decimal
from datetime import timedelta

from django.utils import timezone
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from .models import *
from .serializers import *


# ===================== CSRF EXEMPT SESSION AUTH =====================
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


# ===================== HOME =====================
def home_view(request):
    return render(request, 'home.html')


# ===================== AUTH =====================
@csrf_exempt
@authentication_classes([CsrfExemptSessionAuthentication])
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return Response({"message": "Login successful"}, status=200)

    return Response({"error": "Invalid credentials"}, status=401)


# ===================== PERMISSIONS =====================
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)


# ===================== ADMIN VIEWS =====================
class AdminUserViewSet(viewsets.ModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class AdminBankAccountViewSet(viewsets.ModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication]
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAdminUser]


class AdminLoanViewSet(viewsets.ModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication]
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

        return Response({'message': f'Loan {loan.status}'})

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
    authentication_classes = [CsrfExemptSessionAuthentication]
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
                if user_request.request_type in ['deposit', 'withdrawal'] and account:
                    Transaction.objects.create(
                        account=account,
                        transaction_type=user_request.request_type,
                        amount=Decimal(user_request.amount),
                        description='Request approved by admin'
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

        return Response({'message': 'Request processed'})


# ===================== USER VIEWS =====================
class UserDashboardView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        })


class UserAccountViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication]
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)


class UserTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication]
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(account__user=self.request.user)


class UserLoanViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication]
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)


class UserRequestViewSet(viewsets.ModelViewSet):
    authentication_classes = [CsrfExemptSessionAuthentication]
    serializer_class = UserRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')


# ===================== REGISTER =====================
class RegisterView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data.copy()
        data['role'] = 'user'

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        BankAccount.objects.create(
            user=user,
            account_type=request.data.get('account_type', 'savings'),
            balance=0
        )

        return Response(
            {
                "message": "Registered Successfully",
                "username": user.username
            },
            status=201
        )