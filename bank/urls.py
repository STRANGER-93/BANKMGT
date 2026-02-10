from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import login_view, RegisterView, AdminUserViewSet, AdminBankAccountViewSet, AdminLoanViewSet, AdminRequestViewSet, UserRequestViewSet, UserAccountViewSet, UserTransactionViewSet, UserLoanViewSet

router = DefaultRouter()

# Admin routes
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')
router.register(r'admin/accounts', AdminBankAccountViewSet, basename='admin-accounts')
router.register(r'admin/loans', AdminLoanViewSet, basename='admin-loans')
router.register(r'admin/requests', AdminRequestViewSet, basename='admin-requests')

# User routes
router.register(r'userrequest', UserRequestViewSet, basename='user-request')
router.register(r'user/accounts', UserAccountViewSet, basename='user-accounts')
router.register(r'user/transactions', UserTransactionViewSet, basename='user-transactions')
router.register(r'user/loans', UserLoanViewSet, basename='user-loans')

urlpatterns = [
    # Auth endpoints (must match React)
    path('login/', login_view, name='login'),       # POST /api/login/
    path('register/', RegisterView.as_view(), name='register'),  # POST /api/register/

    # Include router for other API endpoints
    path('', include(router.urls)),
]
