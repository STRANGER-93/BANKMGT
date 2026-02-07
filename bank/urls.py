# banking/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Admin routes
router.register(r'admin/users', views.AdminUserViewSet, basename='admin-users')
router.register(r'admin/accounts', views.AdminBankAccountViewSet, basename='admin-accounts')
router.register(r'admin/loans', views.AdminLoanViewSet, basename='admin-loans')

# User routes
router.register(r'user/accounts', views.UserAccountViewSet, basename='user-accounts')
router.register(r'user/transactions', views.UserTransactionViewSet, basename='user-transactions')
router.register(r'user/loans', views.UserLoanViewSet, basename='user-loans')

urlpatterns = [
    path('', views.home_view, name='home'),
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api-auth/', include('rest_framework.urls')),  # login/logout
]
