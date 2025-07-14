from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone
from .utils import send_sms_otp, send_email_otp

# Create your views here.
def About (request):
    return render(request,'about.html')


def Contect(request):
    return render(request,'contact.html')


def Index(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return render(request, 'index.html')


def Register_Admin(request):
    error = ""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        mobile_number = request.POST['mobile_number']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            error = "Passwords do not match!"
        else:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                error = "Username already exists!"
            elif User.objects.filter(email=email).exists():
                error = "Email already registered!"
            elif AdminRegistration.objects.filter(mobile_number=mobile_number).exists():
                error = "Mobile number already registered!"
            else:
                try:
                    # Delete all existing admin users (staff users)
                    old_admins = User.objects.filter(is_staff=True, is_superuser=True)
                    for old_admin in old_admins:
                        # Delete associated OTP records
                        AdminOTP.objects.filter(user=old_admin).delete()
                        # Delete the user
                        old_admin.delete()
                    
                    # Create new admin user (initially inactive until OTP verification)
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        is_staff=True,
                        is_superuser=True,
                        is_active=False  # Will be activated after OTP verification
                    )
                    
                    # Create OTP record with expiration time
                    otp_record = AdminOTP.objects.create(
                        user=user,
                        mobile_number=mobile_number,
                        otp=''.join(random.choices(string.digits, k=6)),
                        expires_at=timezone.now() + timedelta(minutes=10)
                    )
                    
                    # Send OTP via SMS
                    sms_sent = send_sms_otp(mobile_number, otp_record.otp)
                    
                    if sms_sent:
                        # Store in session for verification
                        request.session['otp_mobile'] = mobile_number
                        request.session['otp_code'] = otp_record.otp
                        request.session['user_id'] = user.id
                        
                        messages.success(request, f"OTP sent successfully to {mobile_number}")
                        return redirect('verify_otp')
                    else:
                        # If SMS fails, delete the user and OTP record
                        user.delete()
                        otp_record.delete()
                        error = "Failed to send OTP. Please try again."
                    
                except Exception as e:
                    error = f"Error creating account: {str(e)}"
    
    d = {'error': error}
    return render(request, 'register_admin.html', d)


def Verify_OTP(request):
    error = ""
    success = ""
    
    # Get OTP details from session
    otp_mobile = request.session.get('otp_mobile')
    otp_code = request.session.get('otp_code')
    user_id = request.session.get('user_id')
    
    if not all([otp_mobile, otp_code, user_id]):
        return redirect('register_admin')
    
    if request.method == 'POST':
        entered_otp = request.POST['otp']
        
        if entered_otp == otp_code:
            try:
                # Verify OTP
                otp_record = AdminOTP.objects.get(mobile_number=otp_mobile)
                otp_record.is_verified = True
                otp_record.save()
                
                # Activate user
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                
                # Create AdminRegistration record
                AdminRegistration.objects.create(
                    user=user,
                    first_name=user.first_name or user.username,
                    last_name=user.last_name or "",
                    email=user.email,
                    mobile_number=otp_mobile,
                    hospital_name="",  # Will be updated later
                    position="Administrator",
                    is_verified=True
                )
                
                # Clear session
                del request.session['otp_mobile']
                del request.session['otp_code']
                del request.session['user_id']
                
                success = "Account verified successfully! You can now login."
                return render(request, 'verify_otp.html', {'success': success})
                
            except Exception as e:
                error = f"Error verifying OTP: {str(e)}"
        else:
            error = "Invalid OTP! Please try again."
    
    d = {'error': error, 'mobile': otp_mobile}
    return render(request, 'verify_otp.html', d)


def Resend_OTP(request):
    otp_mobile = request.session.get('otp_mobile')
    user_id = request.session.get('user_id')
    
    if not all([otp_mobile, user_id]):
        return redirect('register_admin')
    
    try:
        otp_record = AdminOTP.objects.get(mobile_number=otp_mobile)
        # Generate new OTP and expiration time
        otp_record.otp = ''.join(random.choices(string.digits, k=6))
        otp_record.expires_at = timezone.now() + timedelta(minutes=10)
        otp_record.save()
        
        # Send new OTP via SMS
        sms_sent = send_sms_otp(otp_mobile, otp_record.otp)
        
        if sms_sent:
            # Update session
            request.session['otp_code'] = otp_record.otp
            messages.success(request, f"New OTP sent successfully to {otp_mobile}!")
        else:
            messages.error(request, "Failed to send OTP. Please try again.")
        
        return redirect('verify_otp')
        
    except Exception as e:
        messages.error(request, f"Error sending OTP: {str(e)}")
        return redirect('verify_otp')

def Forgot_Password(request):
    error = ""
    success = ""
    
    if request.method == 'POST':
        reset_type = request.POST.get('reset_type', 'mobile')
        
        if reset_type == 'mobile':
            mobile_number = request.POST.get('mobile_number')
            
            if not mobile_number:
                error = "Please enter your mobile number!"
                return render(request, 'forgot_password.html', {'error': error, 'success': success})
            
            try:
                # Find admin registration with this mobile number
                admin_registration = AdminRegistration.objects.get(mobile_number=mobile_number)
                user = admin_registration.user
                
                # Create password reset record with token and expiration
                reset_record = PasswordReset.objects.create(
                    user=user,
                    mobile_number=mobile_number,
                    reset_type='mobile',
                    token=''.join(random.choices(string.ascii_letters + string.digits, k=50)),
                    expires_at=timezone.now() + timedelta(hours=24)
                )
                
                # Send OTP via SMS
                sms_sent = send_sms_otp(mobile_number, reset_record.token[:6])  # Use first 6 chars as OTP
                
                if sms_sent:
                    # Store in session
                    request.session['reset_token'] = reset_record.token
                    request.session['reset_mobile'] = mobile_number
                    request.session['reset_type'] = 'mobile'
                    
                    success = f"Password reset OTP sent to {mobile_number}!"
                    return redirect('reset_password')
                else:
                    # If SMS fails, delete the reset record
                    reset_record.delete()
                    error = "Failed to send OTP. Please try again."
                
            except AdminRegistration.DoesNotExist:
                error = "No admin account found with this mobile number!"
            except Exception as e:
                error = f"Error: {str(e)}"
        
        elif reset_type == 'email':
            email = request.POST.get('email')
            
            if not email:
                error = "Please enter your email address!"
                return render(request, 'forgot_password.html', {'error': error, 'success': success})
            
            try:
                # Find admin registration with this email
                admin_registration = AdminRegistration.objects.get(email=email)
                user = admin_registration.user
                
                # Create password reset record with token and expiration
                reset_record = PasswordReset.objects.create(
                    user=user,
                    email=email,
                    reset_type='email',
                    token=''.join(random.choices(string.ascii_letters + string.digits, k=50)),
                    expires_at=timezone.now() + timedelta(hours=24)
                )
                
                # Store in session for demo (in production, send email)
                request.session['reset_token'] = reset_record.token
                request.session['reset_email'] = email
                request.session['reset_type'] = 'email'
                
                success = "Password reset link sent to your email address!"
                return redirect('reset_password')
                
            except AdminRegistration.DoesNotExist:
                error = "No admin account found with this email address!"
            except Exception as e:
                error = f"Error: {str(e)}"
    
    return render(request, 'forgot_password.html', {'error': error, 'success': success})

def Reset_Password(request):
    error = ""
    success = ""
    
    reset_token = request.session.get('reset_token')
    reset_type = request.session.get('reset_type', 'mobile')
    
    if not reset_token:
        return redirect('forgot_password')
    
    try:
        if reset_type == 'mobile':
            reset_mobile = request.session.get('reset_mobile')
            if not reset_mobile:
                return redirect('forgot_password')
            
            reset_record = PasswordReset.objects.get(
                token=reset_token, 
                mobile_number=reset_mobile, 
                reset_type='mobile',
                is_used=False
            )
        else:  # email
            reset_email = request.session.get('reset_email')
            if not reset_email:
                return redirect('forgot_password')
            
            reset_record = PasswordReset.objects.get(
                token=reset_token, 
                email=reset_email, 
                reset_type='email',
                is_used=False
            )
        
        if reset_record.is_expired():
            error = "Reset link has expired!"
            # Clear session
            if reset_type == 'mobile':
                del request.session['reset_token']
                del request.session['reset_mobile']
                del request.session['reset_type']
            else:
                del request.session['reset_token']
                del request.session['reset_email']
                del request.session['reset_type']
            return render(request, 'reset_password.html', {'error': error})
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password != confirm_password:
                error = "Passwords do not match!"
            elif len(new_password) < 8:
                error = "Password must be at least 8 characters long!"
            else:
                # Update password
                user = reset_record.user
                user.set_password(new_password)
                user.save()
                
                # Mark reset token as used
                reset_record.is_used = True
                reset_record.save()
                
                # Clear session
                if reset_type == 'mobile':
                    del request.session['reset_token']
                    del request.session['reset_mobile']
                    del request.session['reset_type']
                else:
                    del request.session['reset_token']
                    del request.session['reset_email']
                    del request.session['reset_type']
                
                success = "Password reset successfully! You can now login with your new password."
                return render(request, 'reset_password.html', {'success': success})
        
    except PasswordReset.DoesNotExist:
        error = "Invalid reset link!"
        # Clear session
        if reset_type == 'mobile':
            del request.session['reset_token']
            del request.session['reset_mobile']
            del request.session['reset_type']
        else:
            del request.session['reset_token']
            del request.session['reset_email']
            del request.session['reset_type']
    except Exception as e:
        error = f"Error: {str(e)}"
    
    context = {
        'error': error, 
        'success': success,
        'reset_type': reset_type
    }
    return render(request, 'reset_password.html', context)


def Login(request):
    error=""
    success=""
    if request.method=='POST':
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        try:
            if user and user.is_staff and user.is_active:
                login(request, user)
                success = "Login successful! Redirecting to dashboard..."
            elif user and user.is_staff and not user.is_active:
                error = "Account not verified. Please verify your email with OTP first."
            else:
                error = "yes"
        except:
            error = "yes"
    d ={'error': error, 'success': success}
    return render(request, 'login.html' ,d)



def Logout_admin(request):
    if not request.user.is_staff:
        return redirect ('login')
    logout(request)
    return redirect('login')

def Admin_Profile(request):
    if not request.user.is_staff:
        return redirect('login')
    
    try:
        admin_profile = AdminRegistration.objects.get(user=request.user)
    except AdminRegistration.DoesNotExist:
        admin_profile = None
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone_number = request.POST.get('phone_number', '')
        hospital_name = request.POST.get('hospital_name', '')
        position = request.POST.get('position', '')
        
        if admin_profile:
            admin_profile.first_name = first_name
            admin_profile.last_name = last_name
            admin_profile.phone_number = phone_number
            admin_profile.hospital_name = hospital_name
            admin_profile.position = position
            admin_profile.save()
        else:
            AdminRegistration.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                email=request.user.email,
                phone_number=phone_number,
                hospital_name=hospital_name,
                position=position,
                is_verified=True
            )
        
        messages.success(request, "Profile updated successfully!")
        return redirect('admin_profile')
    
    context = {
        'admin_profile': admin_profile
    }
    return render(request, 'admin_profile.html', context)

def Delete_Admin_Profile(request):
    if not request.user.is_staff:
        return redirect('login')
    
    try:
        admin_profile = AdminRegistration.objects.get(user=request.user)
        admin_profile.delete()
        messages.success(request, "Profile deleted successfully!")
    except AdminRegistration.DoesNotExist:
        messages.error(request, "No profile found to delete!")
    except Exception as e:
        messages.error(request, f"Error deleting profile: {str(e)}")
    
    return redirect('admin_dashboard')
    
    
def View_Doctor(request):
  if not request.user.is_staff:
      return redirect('login')
  doc = Doctor.objects.all()
  d ={'doc': doc}
  return render(request, 'view_doctor.html', d)


  
def Add_Doctor(request):
    error = ""
    if not request.user.is_staff:
        return redirect('login')
    if request.method == 'POST':
        name = request.POST['name']
        contact_number = request.POST['contact_number']
        specialization = request.POST['specialization']
        try:
            Doctor.objects.create(
                name=name,
                contact_number=contact_number,
                specialization=specialization
            )
            error = "no"
        except Exception as e:
            print("Error saving doctor:", e)
            error = "yes"
    d = {'error': error}
    return render(request, 'add_doctor.html', d)


def Delete_Doctor(request, doctor_id):
    error=""
    if not request.user.is_staff:
        return redirect('login')
    doctor = Doctor.objects.get(id=doctor_id)
    doctor.delete()
    return redirect('view_doctor')


def Admin_Dashboard(request):
    if not request.user.is_staff:
        return redirect('login')
    
    doctor_count = Doctor.objects.count()
    patient_count = Patient.objects.count()
    appointment_count = Appointment.objects.count()
    
    # Get admin profile
    try:
        admin_profile = AdminRegistration.objects.get(user=request.user)
    except AdminRegistration.DoesNotExist:
        admin_profile = None
    
    context = {
        'doctor_count': doctor_count,
        'patient_count': patient_count,
        'appointment_count': appointment_count,
        'admin_profile': admin_profile,
    }
    return render(request, 'admin_dashboard.html', context)


    


def Add_Patient(request):
    error = ""
    if not request.user.is_staff:
        return redirect('login')
    if request.method == 'POST':
        name = request.POST['name']
        gender = request.POST['gender']
        mobile_number = request.POST['mobile_number']
        address = request.POST['address']
        try:
            Patient.objects.create(
                name=name,
                gender=gender,
                mobile_number=mobile_number,
                address=address
            )
            error = "no"
        except Exception as e:
            print("Error saving patient:", e)
            error = "yes"
    d = {'error': error}
    return render(request, 'add_patient.html', d)

def View_Patient(request):
    if not request.user.is_staff:
        return redirect('login')
    patients = Patient.objects.all()
    d = {'patients': patients}
    return render(request, 'view_patient.html', d)


    


def Add_Appointment(request):
    error = ""
    if not request.user.is_staff:
        return redirect('login')
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    if request.method == 'POST':
        patient_id = request.POST['patient']
        doctor_id = request.POST['doctor']
        appointment_date = request.POST['appointment_date']
        appointment_time = request.POST['appointment_time']
        try:
            patient = Patient.objects.get(id=patient_id)
            doctor = Doctor.objects.get(id=doctor_id)
            Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )
            error = "no"
        except Exception as e:
            print("Error saving appointment:", e)
            error = "yes"
    d = {'error': error, 'patients': patients, 'doctors': doctors}
    return render(request, 'add_appointment.html', d)

def View_Appointment(request):
    if not request.user.is_staff:
        return redirect('login')
    appointments = Appointment.objects.select_related('patient', 'doctor').all()
    d = {'appointments': appointments}
    return render(request, 'view_appointment.html', d)


def Delete_Appointment(request, appointment_id):
    if not request.user.is_staff:
        return redirect('login')
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.delete()
    except Appointment.DoesNotExist:
        pass
    return redirect('view_appointment')


    

