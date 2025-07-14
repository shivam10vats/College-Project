"""
URL configuration for HospitalManagementSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path 
from hospital.views import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', About,name='about'),
    path('', Index, name='home'),
    path('admin_login/', Login, name='login'),
    path('admin_register/', Register_Admin, name='register_admin'),
    path('verify_otp/', Verify_OTP, name='verify_otp'),
    path('resend_otp/', Resend_OTP, name='resend_otp'),
    path('forgot_password/', Forgot_Password, name='forgot_password'),
    path('reset_password/', Reset_Password, name='reset_password'),
    path('logout/', Logout_admin, name='logout'),
    path('admin_profile/', Admin_Profile, name='admin_profile'),
    path('delete_admin_profile/', Delete_Admin_Profile, name='delete_admin_profile'),
    path('contact/', Contect, name='contact'),
    path('view_doctor/', View_Doctor, name='view_doctor'),
    path('add_doctor/', Add_Doctor, name='add_doctor'),
    path('delete_doctor/<int:doctor_id>/', Delete_Doctor, name='delete_doctor'),
    path('admin_dashboard/', Admin_Dashboard, name='admin_dashboard'),
    path('add_patient/', Add_Patient, name='add_patient'),
    path('view_patient/', View_Patient, name='view_patient'),
    path('add_appointment/', Add_Appointment, name='add_appointment'),
    path('view_appointment/', View_Appointment, name='view_appointment'),
    path('delete_appointment/<int:appointment_id>/', Delete_Appointment, name='delete_appointment'),
]
