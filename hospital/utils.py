"""
Utility functions for SMS and Email functionality
"""
import logging
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

def send_sms_otp(mobile_number, otp):
    """
    Send OTP via SMS
    In production, integrate with SMS providers like Twilio, Fast2SMS, etc.
    """
    try:
        # TODO: Replace with actual SMS provider integration
        # Example with Twilio:
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # message = client.messages.create(
        #     body=f"Your OTP is {otp}",
        #     from_=settings.TWILIO_PHONE_NUMBER,
        #     to=f"+91{mobile_number}"
        # )
        
        # For now, just log the OTP (for development/testing)
        print(f"\n{'='*50}")
        print(f"📱 SMS OTP SENT")
        print(f"📞 Mobile: {mobile_number}")
        print(f"🔢 OTP: {otp}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        logger.info(f"SMS OTP {otp} would be sent to {mobile_number}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending SMS OTP: {str(e)}")
        return False

def send_email_reset_link(email, reset_link):
    """
    Send password reset link via email
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = "Password Reset Request - Hospital Management System"
        message = f"""
        Hello,
        
        You have requested to reset your password for the Hospital Management System.
        
        Click the following link to reset your password:
        {reset_link}
        
        This link will expire in 24 hours.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        Hospital Management System Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email reset link: {str(e)}")
        return False

def send_email_otp(email, otp):
    """
    Send OTP via email
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = "OTP Verification - Hospital Management System"
        message = f"""
        Hello,
        
        Your OTP for verification is: {otp}
        
        This OTP will expire in 10 minutes.
        
        If you didn't request this OTP, please ignore this email.
        
        Best regards,
        Hospital Management System Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        logger.info(f"Email OTP {otp} sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email OTP: {str(e)}")
        return False 