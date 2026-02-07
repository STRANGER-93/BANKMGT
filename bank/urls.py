# banking/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import login_view, RegisterView

router = DefaultRouter()

# Admin routes
router.register(r'admin/users', views.AdminUserViewSet, basename='admin-users')
router.register(r'admin/accounts', views.AdminBankAccountViewSet, basename='admin-accounts')
router.register(r'admin/loans', views.AdminLoanViewSet, basename='admin-loans')
router.register(r'admin/requests', views.AdminRequestViewSet, basename='admin-requests')

# User routes
# User routes
router.register(r'userrequest', views.UserRequestViewSet, basename='user-request')

router.register(r'user/accounts', views.UserAccountViewSet, basename='user-accounts')
router.register(r'user/transactions', views.UserTransactionViewSet, basename='user-transactions')
router.register(r'user/loans', views.UserLoanViewSet, basename='user-loans')

urlpatterns = [
    path('', views.home_view, name='home'),
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'), 
]
