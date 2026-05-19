from django.urls import path
from .views import SignupView, LoginView, LogoutView, AdminOnlyView, SellerOnlyView, SellerOrSupplierView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='api-signup'),
    path('login/', LoginView.as_view(), name='api-login'),
    path('logout/', LogoutView.as_view(), name='api-logout'),
    
    # Example Endpoints
    path('admin-only/', AdminOnlyView.as_view(), name='admin-only'),
    path('seller-only/', SellerOnlyView.as_view(), name='seller-only'),
    path('seller-or-supplier/', SellerOrSupplierView.as_view(), name='seller-or-supplier'),
    
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]