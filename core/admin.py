from django.contrib import admin
from .models import MSAG, DSLCard, DSLPort, Customer, Complaint, DSLPortHistory, CustomerComplaint
from django.utils.html import format_html
from django import forms
from django.db.models import Q

# DSLCardAdmin
class DSLCardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'msag__name', 'msag__location', 'total_ports', 'card_type')
    list_filter = ('card_type',)
    def msag__name(self, obj):
        return obj.msag.name
    msag__name.short_description = 'MSAG Name'

    def msag__location(self, obj):
        return obj.msag.location
    msag__location.short_description = 'MSAG Location'

    def total_ports(self, obj):
        return obj.ports.count()
    total_ports.short_description = 'Total Ports'

    def msag__name(self, obj):
        return obj.msag.name
    msag__name.short_description = 'MSAG Name'

# Register other models
admin.site.register(MSAG)
admin.site.register(DSLCard, DSLCardAdmin)
admin.site.register(DSLPort)
admin.site.register(Customer)
admin.site.register(Complaint)
admin.site.register(DSLPortHistory)
admin.site.register(CustomerComplaint)

# DSLRequestAdmin
from .forms import DSLRequestForm
from .models import DSLRequest, ModemInventory, WorkOrder, DigitalDocuments

class DSLRequestAdmin(admin.ModelAdmin):
    form = DSLRequestForm
    list_display = ['customer', 'package', 'contact']
    list_filter = ['package']
    search_fields = ['customer__name', 'address', 'contact']
    ordering = ['customer']

admin.site.register(DSLRequest, DSLRequestAdmin)
admin.site.register(ModemInventory)
admin.site.register(DigitalDocuments)

# Custom WorkOrder Form
class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'msag' in self.initial:
            msag = self.initial['msag']
            self.fields['dsl_port'].queryset = DSLPort.objects.filter(msag=msag, status='Available')
        else:
            self.fields['dsl_port'].queryset = DSLPort.objects.none()

from django.contrib import admin
from django import forms
from django.urls import reverse
from .models import WorkOrder, DSLPort, DSLCard
from django.db.models import Q

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically filter the DSLPort queryset based on the selected DSLCard
        if 'card_number' in self.data:  # When the form is submitted
            try:
                card_id = int(self.data.get('card_number'))
                self.fields['dsl_port'].queryset = DSLPort.objects.filter(
                    dsl_card_id=card_id, status=False
                )
            except (ValueError, TypeError):
                self.fields['dsl_port'].queryset = DSLPort.objects.none()
        elif self.instance.pk:  # When editing an existing WorkOrder
            self.fields['dsl_port'].queryset = DSLPort.objects.filter(
                dsl_card=self.instance.card_number, status=False
            )
        else:
            self.fields['dsl_port'].queryset = DSLPort.objects.none()


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    form = WorkOrderForm
    list_display = ('dsl_request', 'card_number', 'card_type', 'dsl_port', 'status')
    list_filter = ('status',)
    search_fields = ('dsl_request__customer__name', 'card_number__number')
    class Media:
        js = ('js/workorder_admin.js',) 

    def card_type(self, obj):
        return obj.card_number.card_type
    card_type.short_description = 'Card Type'




from django.contrib import admin
from .models import DSLPort, Customer

class DSLPortAdmin(admin.ModelAdmin):
    list_display = ('port_number', 'dsl_card', 'status', 'customer')
    list_filter = ('dsl_card', 'status')
    search_fields = ('port_number', 'dsl_card__card_number', 'customer__name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('dsl_card', 'customer')




from django.contrib import admin
from .models import Customer, DSLPort, ModemInventory


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact', 'get_assigned_port', 'get_assigned_modem')
    search_fields = ('name', 'contact', 'address')

    def get_assigned_port(self, obj):
        """Retrieve the port assigned to the customer."""
        port = DSLPort.objects.filter(customer=obj).first()
        return f"Port {port.port_number} on Card {port.dsl_card.card_number}" if port else "No Port Assigned"

    def get_assigned_modem(self, obj):
        """Retrieve the modem assigned to the customer."""
        port = DSLPort.objects.filter(customer=obj).first()
        return port.modem.serial_number if port and port.modem else "No Modem Assigned"

    get_assigned_port.short_description = "Assigned Port"
    get_assigned_modem.short_description = "Assigned Modem"


# Register the customized admin
#admin.site.register(Customer, CustomerAdmin)
from django.contrib import admin
from .models import DSLPortHistory


class DSLPortHistoryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'port', 'allocation_date', 'deallocation_date', 'is_active')
    list_filter = ('is_active', 'allocation_date', 'deallocation_date')
    search_fields = ('customer__name', 'port__port_number')