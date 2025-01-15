from django.test import TestCase

# Create your tests here.
from core.models import DSLPort, Customer

port = DSLPort.objects.get(port_number=1)
customer = Customer.objects.get(name='John Doe')
port.customer = customer
port.status = True
port.save()
