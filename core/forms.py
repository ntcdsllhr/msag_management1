from django import forms
from django.db.models import Q
from .models import DSLRequest, WorkOrder, DSLPort, ModemInventory


def get_available_ports(msag=None):
    queryset = DSLPort.objects.filter(status=False, customer__isnull=True)
    if msag:
        queryset = queryset.filter(dsl_card__msag=msag)  # Adjust as needed
    return queryset


class DSLRequestForm(forms.ModelForm):
    class Meta:
        model = DSLRequest
        fields = ['customer', 'address', 'package', 'contact']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'package': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ModemIssuanceForm(forms.Form):
    modem = forms.ModelChoiceField(
        queryset=ModemInventory.objects.filter(status='Available'),
        label="Select Modem",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        msag = kwargs.pop('msag', None)  # Pass MSAG dynamically if needed
        super().__init__(*args, **kwargs)

        # Default DSL Port queryset to empty
        self.fields['dsl_port'].queryset = DSLPort.objects.none()

        # Populate DSL Port based on the existing instance
        if self.instance and self.instance.dsl_card:
            existing_card = self.instance.dsl_card
            self.fields['dsl_port'].queryset = DSLPort.objects.filter(
                dsl_card=existing_card, status=False, customer__isnull=True
            )

        # Handle filtering based on DSL card selection in the form
        elif 'dsl_card' in self.data:
            try:
                dsl_card_id = int(self.data.get('dsl_card'))
                self.fields['dsl_port'].queryset = DSLPort.objects.filter(
                    dsl_card_id=dsl_card_id, status=False, customer__isnull=True
                )
            except (ValueError, TypeError):
                pass  # Ignore invalid DSL card ID

        # Handle filtering based on MSAG, if provided
        elif msag:
            self.fields['dsl_port'].queryset = DSLPort.objects.filter(
                dsl_card__msag=msag, status=False, customer__isnull=True
            )


from django import forms
from .models import DSLCard

class DSLCardForm(forms.ModelForm):
    class Meta:
        model = DSLCard
        fields = ['card_number', 'msag', 'card_type']
        widgets = {
            'card_type': forms.Select(attrs={'class': 'form-control'}),
        }




from django import forms
from .models import DSLPort

class DSLPortForm(forms.ModelForm):
    class Meta:
        model = DSLPort
        fields = ['port_number', 'dsl_card', 'customer']

    def clean(self):
        cleaned_data = super().clean()
        customer = cleaned_data.get('customer')
        status = cleaned_data.get('status')
        
        # Ensure that a port assigned to a customer is activated
        if customer and not status:
            cleaned_data['status'] = True

        return cleaned_data
