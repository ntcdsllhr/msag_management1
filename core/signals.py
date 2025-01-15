from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import DSLCard, DSLPort, DSLPortHistory

@receiver(post_save, sender=DSLCard)
def create_ports_for_dsl_card(sender, instance, created, **kwargs):
    if created:  # Only when a new card is created
        # Create 64 ports numbered from 0 to 63
        ports = [DSLPort(port_number=i, dsl_card=instance) for i in range(64)]
        DSLPort.objects.bulk_create(ports)  # Efficiently create ports in bulk



from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import DSLPort

@receiver(post_save, sender=DSLPort)
def activate_port(sender, instance, **kwargs):
    # Automatically activate port if a customer is assigned
    if instance.customer and not instance.status:
        instance.status = True
        instance.save(update_fields=['status'])

@receiver(pre_delete, sender=DSLPort)
def deactivate_port_on_delete(sender, instance, **kwargs):
    # Deactivate port when the instance is deleted
    if instance.status:
        instance.status = False
        instance.customer = None
        instance.save(update_fields=['status', 'customer'])



@receiver(pre_save, sender=DSLPort)
def handle_port_history(sender, instance, **kwargs):
    """
    Handles port allocation and deallocation history updates.
    """
    if instance.pk:  # Check if this is an update
        old_instance = DSLPort.objects.get(pk=instance.pk)

        # Case 1: Port is allocated to a customer
        if not old_instance.customer and instance.customer:
            DSLPortHistory.objects.create(
                customer=instance.customer,
                port=instance,
                is_active=True
            )

        # Case 2: Port is deallocated from a customer
        if old_instance.customer and not instance.customer:
            DSLPortHistory.objects.filter(
                customer=old_instance.customer,
                port=old_instance,
                is_active=True
            ).update(deallocation_date=timezone.now(), is_active=False)
