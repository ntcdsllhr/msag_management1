from django.db import models
from django.core.exceptions import ValidationError


class MSAG(models.Model):
    name = models.CharField(max_length=255)
    location = models.TextField()
    total_cards = models.IntegerField()
    spare_ports = models.IntegerField()

    def __str__(self):
        return self.name


class DSLCard(models.Model):
    CARD_TYPES = [
        ('ADSL', 'ADSL'),
        ('VDSL', 'VDSL'),
    ]
    card_number = models.IntegerField()
    msag = models.ForeignKey(MSAG, on_delete=models.CASCADE, related_name='cards')
    total_ports = models.IntegerField(default=64)
    card_type = models.CharField(max_length=4, choices=CARD_TYPES, default='ADSL') 

    class Meta:
        unique_together = ('msag', 'card_number')  # Ensure unique card numbers within an MSAG

    def clean(self):
        if self.total_ports != 64:
            raise ValidationError("DSL cards must have exactly 64 ports.")

    def __str__(self):
        return f"Card {self.card_type} in {self.msag.name}"


from django.db import models
from django.core.exceptions import ValidationError


class DSLPort(models.Model):
    port_number = models.IntegerField()
    dsl_card = models.ForeignKey('DSLCard', on_delete=models.CASCADE, related_name='ports')
    customer = models.OneToOneField('Customer', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.BooleanField(default=False)  # False means inactive, True means active

    class Meta:
        unique_together = ('dsl_card', 'port_number')  # Ensure no duplicate ports on the same DSLCard

    def clean(self):
        # Validate port number range
        if not (0 <= self.port_number < 64):
            raise ValidationError("Port number must be between 0 and 63.")

        # Ensure the DSLCard does not have more than 64 ports
        if self.dsl_card.ports.exclude(pk=self.pk).count() >= 64:
            raise ValidationError("A DSL card cannot have more than 64 ports.")

        # Prevent reassigning an active port to a different customer
        if self.pk:
            current_instance = DSLPort.objects.get(pk=self.pk)
            if current_instance.status and current_instance.customer and current_instance.customer != self.customer:
                raise ValidationError(f"Port {self.port_number} is already assigned to another customer.")

    def save(self, *args, **kwargs):
        # Automatically activate or deactivate the port based on customer assignment
        if not self.customer:
            self.status = False  # Deactivate the port if no customer is assigned
        else:
            self.status = True   # Activate the port if a customer is assigned
        super().save(*args, **kwargs)

    def deactivate(self):
        """Custom method to deactivate the port manually."""
        self.customer = None
        self.status = False
        self.save(update_fields=['customer', 'status'])

    def __str__(self):
        return f"Port {self.port_number} on {self.dsl_card} ({'Active' if self.status else 'Inactive'})"





class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)
    dsl_enabled = models.BooleanField(default=False)
    ipv6_enabled = models.BooleanField(default=False)
    modem_brand = models.CharField(max_length=255, null=True, blank=True)
    msag = models.ForeignKey(MSAG, on_delete=models.CASCADE, related_name='customers')
    email = models.EmailField()

    def clean(self):
        if len(self.phone_number) < 10:
            raise ValidationError("Phone number must be at least 10 digits long.")

    def __str__(self):
        return self.name


class Complaint(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='general_complaints')
    type = models.CharField(max_length=255)
    reason = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=False)  # False means unresolved, True means resolved

    def __str__(self):
        return f"Complaint by {self.customer.name}: {self.type}"


class DSLPortHistory(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='port_history')
    port = models.ForeignKey('DSLPort', on_delete=models.CASCADE, related_name='port_history')
    allocation_date = models.DateTimeField(auto_now_add=True)
    deallocation_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)  # Indicates if the allocation is still active

    class Meta:
        verbose_name = 'DSL Port Allocation History'
        verbose_name_plural = 'DSL Port Allocation Histories'

    def __str__(self):
        return f"Port {self.port.port_number} allocated to {self.customer.name} on {self.allocation_date}"


class CustomerComplaint(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='detailed_complaints')
    complaint_date = models.DateTimeField(auto_now_add=True)
    complaint_text = models.TextField()
    status = models.CharField(max_length=50, choices=[('Open', 'Open'), ('Closed', 'Closed')], default='Open')
    resolution = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Customer Complaint'
        verbose_name_plural = 'Customer Complaints'

    def __str__(self):
        return f"Complaint from {self.customer.name} on {self.complaint_date} - Status: {self.status}"



        #new installation eco system 
    
class DSLRequest(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='dsl_requests')
    address = models.TextField()
    package = models.CharField(max_length=255)
    contact = models.CharField(max_length=20)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')])
    def __str__(self):
        return f"Work Order for {self.customer.name}"



class ModemInventory(models.Model):
       brand = models.CharField(max_length=255)
       serial_number = models.CharField(max_length=255, unique=True)
       issued_to = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
       issue_date = models.DateTimeField(null=True, blank=True)
       status = models.CharField(max_length=50, choices=[('Available', 'Available'), ('Issued', 'Issued')], default='Available')    
       def __str__(self):
        return f"Work Order for {self.serial_number}"





class DigitalDocuments(models.Model):
       customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
       document_type = models.CharField(max_length=255)
       file = models.FileField(upload_to='documents/')
       uploaded_at = models.DateTimeField(auto_now_add=True)


class WorkOrder(models.Model):
    dsl_request = models.OneToOneField(DSLRequest, on_delete=models.CASCADE, related_name='work_order')
    technician = models.CharField(max_length=255)
    phone_number = models.ForeignKey(Customer, on_delete=models.CASCADE)
    msag = models.ForeignKey(MSAG, on_delete=models.CASCADE, related_name='work_orders')
    card_number = models.ForeignKey(DSLCard, on_delete=models.CASCADE, related_name='work_orders')  # Use this field to determine card_type
    dsl_port = models.OneToOneField(DSLPort, on_delete=models.SET_NULL, null=True, blank=True, related_name='work_orders')
    modem = models.OneToOneField(ModemInventory, on_delete=models.SET_NULL, null=True, blank=True, related_name='work_orders')
    scheduled_date = models.DateTimeField()
    completion_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[('Assigned', 'Assigned'), ('In Progress', 'In Progress'), ('Completed', 'Completed')],
        default='Assigned'
    )
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"WorkOrder for {self.dsl_request.customer.name} - Status: {self.status}"


    def clean(self):
        if self.dsl_port and WorkOrder.objects.filter(dsl_port=self.dsl_port).exclude(pk=self.pk).exists():
            raise ValidationError(f"DSL Port {self.dsl_port.port_number} is already assigned to another work order.")

        if self.modem and self.modem.status != 'Available':
            raise ValidationError(f"Modem {self.modem.serial_number} is already issued and cannot be reassigned.")

    def update_status(self, new_status):
        valid_transitions = {
            'Assigned': ['In Progress'],
            'In Progress': ['Completed'],
        }
        if new_status not in valid_transitions.get(self.status, []):
            raise ValidationError(f"Cannot transition from {self.status} to {new_status}.")
        self.status = new_status
        self.save()

    def __str__(self):
        customer_name = self.dsl_request.customer.name if self.dsl_request and self.dsl_request.customer else "Unknown Customer"
        return f"Work Order for {customer_name} - Status: {self.status}"


