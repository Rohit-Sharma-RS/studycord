# Update in utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_verification_email(user, token, request):
    """Send an email verification link to the user."""
    verification_url = f"{request.scheme}://{request.get_host()}/verify-email/{token}/"
    
    context = {
        'user': user,
        'verification_url': verification_url,
    }
    
    # Change the template path to match your directory structure
    html_message = render_to_string('base/email/verification_email.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject='Verify your email address',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_password_reset_email(user, token, request):
    """Send a password reset link to the user."""
    reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{token}/"
    
    context = {
        'user': user,
        'reset_url': reset_url,
    }
    
    # Change the template path to match your directory structure
    html_message = render_to_string('base/email/password_reset_email.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject='Reset your password',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False