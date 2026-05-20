"""
URLs de usuarios - AudioPro
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, ProfileView, ChangePasswordView, UserAdminViewSet

router = DefaultRouter()
router.register(r'admin', UserAdminViewSet, basename='user-admin')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('', include(router.urls)),
]
