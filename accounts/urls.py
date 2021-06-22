from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('forgotPassword/', views.forgot_password, name='forgot_password'),
    

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset_passwordValidation/<uidb64>/<token>/', views.reset_passwordValidation, name='reset_passwordValidation'),
    path('resetPassword/', views.reset_password, name='reset_password'),

]