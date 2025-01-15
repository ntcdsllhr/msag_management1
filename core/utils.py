from .models import DSLPort

def get_available_ports(dsl_card=None):
    queryset = DSLPort.objects.filter(status=False, customer__isnull=True)
    if dsl_card:
        queryset = queryset.filter(dsl_card=dsl_card)
    return queryset


from django.core.mail import send_mail

def send_email(subject, message, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email='ntcdsllhr@gmail.com',  # Replace with your email
        recipient_list=["azmatntc@gmail.com"],
        fail_silently=False,
    )
