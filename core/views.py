from django.shortcuts import render
from .models import MSAG, Customer, Complaint

from django.shortcuts import render
from .models import Customer, Complaint, MSAG, WorkOrder

def dashboard(request):
    total_customers = Customer.objects.count()
    resolved_complaints = Complaint.objects.filter(status=True).count()
    active_ports = Customer.objects.filter(dsl_enabled=True).count()

    labels = [msag.name for msag in MSAG.objects.all()]
    data = [msag.customers.count() for msag in MSAG.objects.all()]

    # Retrieve all work orders
    work_orders = WorkOrder.objects.all()

    return render(request, 'dashboard.html', {
        'total_customers': total_customers,
        'resolved_complaints': resolved_complaints,
        'active_ports': active_ports,
        'labels': labels,
        'data': data,
        'work_orders': work_orders,  # Pass all work orders to the template
    })




# views.py
from django.shortcuts import render, redirect
from .forms import DSLRequestForm

def new_connection_request(request):
    if request.method == 'POST':
        form = DSLRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Replace with your desired redirect URL
    else:
        form = DSLRequestForm()
    return render(request, 'new_connection_request.html', {'form': form})





# views.py
from .forms import ModemIssuanceForm
from .models import ModemInventory, DSLRequest
from django.shortcuts import render, redirect 
from django.utils import timezone 
from .models import DSLRequest 
from .forms import ModemIssuanceForm



def issue_modem(request, request_id):
    dsl_request = DSLRequest.objects.get(id=request_id)
    if request.method == 'POST':
        form = ModemIssuanceForm(request.POST)
        if form.is_valid():
            modem = form.cleaned_data['modem']
            modem.status = 'Issued'
            modem.issued_to = dsl_request.customer
            modem.issue_date = timezone.now()
            modem.save()
            dsl_request.status = 'In Progress'
            dsl_request.save()
            return redirect('dashboard')
    else:
        form = ModemIssuanceForm()
    return render(request, 'issue_modem.html', {'form': form, 'dsl_request': dsl_request})





# views.py
from .models import WorkOrder
from django.shortcuts import get_object_or_404

def assign_technician(request, work_order_id):
    work_order = get_object_or_404(WorkOrder, id=work_order_id)
    if request.method == 'POST':
        technician_name = request.POST['technician']
        work_order.technician = technician_name
        work_order.status = 'Assigned'
        work_order.save()
        return redirect('dashboard')
    return render(request, 'assign_technician.html', {'work_order': work_order})


from django.db.models import Count, Q
from django.shortcuts import render
from .models import MSAG, Customer, Complaint, DSLPort, DSLRequest, WorkOrder

def comprehensive_report(request):
    # Aggregate data
    total_customers = Customer.objects.count()
    active_customers = Customer.objects.filter(dsl_enabled=True).count()
    inactive_customers = total_customers - active_customers
    resolved_complaints = Complaint.objects.filter(status=True).count()
    unresolved_complaints = Complaint.objects.filter(status=False).count()
    total_requests = DSLRequest.objects.count()
    pending_requests = DSLRequest.objects.filter(status='Pending').count()
    completed_requests = DSLRequest.objects.filter(status='Completed').count()
    total_work_orders = WorkOrder.objects.count()
    completed_work_orders = WorkOrder.objects.filter(status='Completed').count()
    
    msag_data = MSAG.objects.annotate(
        total_customers=Count('customers'),
        active_ports=Count('customers', filter=Q(customers__dsl_enabled=True)),
    )

    # Data for MSAG chart
    msag_labels = [msag.name for msag in msag_data]
    msag_customers_data = [msag.total_customers for msag in msag_data]
    msag_active_ports_data = [msag.active_ports for msag in msag_data]

    # Render to the report template
    return render(request, 'comprehensive_report.html', {
        'total_customers': total_customers,
        'active_customers': active_customers,
        'inactive_customers': inactive_customers,
        'resolved_complaints': resolved_complaints,
        'unresolved_complaints': unresolved_complaints,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
        'total_work_orders': total_work_orders,
        'completed_work_orders': completed_work_orders,
        'msag_labels': msag_labels,
        'msag_customers_data': msag_customers_data,
        'msag_active_ports_data': msag_active_ports_data,
    })





from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from .models import WorkOrder, DSLPort


from django.http import FileResponse, HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from datetime import datetime
from io import BytesIO


def generate_cpe_receipt(request, work_order_id):
    # Fetch the work order and related details
    work_order = WorkOrder.objects.get(id=work_order_id)
    dsl_request = work_order.dsl_request
    customer = dsl_request.customer
    dsl_port = work_order.dsl_port
    modem = work_order.modem
    msag = work_order.msag

    # Create the PDF response
    buffer = BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=10,
        bottomMargin=10
    )
    elements = []
    styles = getSampleStyleSheet()
    custom_center_style = ParagraphStyle(
        name='Center',
        parent=styles['Normal'],
        alignment=1,
        fontSize=9,
        spaceBefore=2,
        spaceAfter=2
    )

    # Header Section with Logo and Title
    logo_path = "static/images/ntc_logo.png"  # Replace with actual path to your logo
    header_table_data = [
        [
            Image(logo_path, width=50, height=50),
            Paragraph("<b>NATIONAL TELECOMMUNICATION CORPORATION</b><br/>"
                      "Ministry of IT & Telecom, Govt of Pakistan<br/>"
                      "Divisional Engineer Phones<br/>"
                      "NTC Regional Building, 6-Race Course Road, Lahore<br/>"
                      "Phone: 042-99203536 | Fax: 042-99203535",
                      styles['Normal'])
        ]
    ]
    header_table = Table(header_table_data, colWidths=[60, 400])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 5))

    # Document Title
    elements.append(Paragraph(
        f"<b>CPE Issue/Receipt Form for Service Activation</b><br/>Form No.: DNL/{work_order_id}<br/>"
        f"Date: {datetime.now().strftime('%Y-%m-%d')}",
        styles['Heading2']
    ))
    elements.append(Spacer(1, 5))

    # Work Order Information Section
    elements.append(Paragraph("Work Order Details", styles['Heading3']))
    work_order_info = [
        ["Field", "Details"],
        ["Work Order ID", work_order.id],
        ["Technician", work_order.technician],
        ["MSAG Name", msag.name],
        ["MSAG Location", msag.location],
        ["Scheduled Date", work_order.scheduled_date.strftime('%Y-%m-%d')],
        ["Completion Date", work_order.completion_date.strftime('%Y-%m-%d') if work_order.completion_date else "Pending"],
        ["Status", work_order.status],
    ]
    elements.append(create_table(work_order_info))
    elements.append(Spacer(1, 5))

    # Customer Information Section
    elements.append(Paragraph("Customer Information", styles['Heading3']))
    customer_info = [
        ["Field", "Details"],
        ["Name", customer.name],
        ["Phone Number", customer.phone_number],
        ["Address", dsl_request.address],
        ["Email", customer.email],
    ]
    elements.append(create_table(customer_info))
    elements.append(Spacer(1, 5))
    # Signature Section
    elements.append(Paragraph("Signatures", styles['Heading3']))
    signature_table_data = [
        ["Technician Signature", "", "Customer Signature & Stamp"],
        ["", "", ""],
        ["", "", ""],  # Leave space for actual signatures
    ]
    signature_table = Table(signature_table_data, colWidths=[150, 100, 150])
    signature_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(signature_table)
    # DSL Port and Modem Details
    elements.append(Paragraph("Assigned Equipment Details", styles['Heading3']))
    equipment_info = [
        ["Field", "Details"],
        ["DSL Port", f"Card {dsl_port.dsl_card.card_type}, Port {dsl_port.port_number}" if dsl_port else "Not Assigned"],
        ["Modem", f"{modem.brand}, Serial No. {modem.serial_number}" if modem else "Not Issued"],
    ]
    elements.append(create_table(equipment_info))
    elements.append(Spacer(1, 5))

    # Signature Section
    elements.append(Paragraph("Signatures", styles['Heading3']))
    signature_table_data = [
        ["Divisional Engineer Phones NTC Lahore", "", "Divisional Engineer Data Comm NTC Lahore"],
        ["", "", ""],
        ["", "", ""],  # Leave space for actual signatures
    ]
    signature_table = Table(signature_table_data, colWidths=[150, 100, 150])
    signature_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(signature_table)

    # Generate PDF
    pdf.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'CPE_Receipt_{customer.name}.pdf')


def create_table(data, colWidths=[120, 250]):
    """Helper function to create a styled table."""
    table = Table(data, colWidths=colWidths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    return table



def create_work_order(request, dsl_request_id):
    dsl_request = DSLRequest.objects.get(id=dsl_request_id)
    customer = dsl_request.customer
    available_modem = ModemInventory.objects.filter(status='Available').first()
    available_port = DSLPort.objects.filter(status=False, dsl_card__msag=customer.msag).first()

    if not available_modem or not available_port:
        return HttpResponse("No available resources to complete the work order.", status=400)

    work_order = WorkOrder.objects.create(
        dsl_request=dsl_request,
        technician="John Doe",
        msag=customer.msag,
        dsl_port=available_port,
        modem=available_modem,
        scheduled_date=datetime.now()
    )

    available_modem.status = 'Issued'
    available_modem.issued_to = customer
    available_modem.issue_date = datetime.now()
    available_modem.save()

    available_port.status = True
    available_port.customer = customer
    available_port.save()

    return redirect('work_order_detail', pk=work_order.id)




from django.http import JsonResponse
from .models import DSLPort

def get_available_ports(request):
    msag_id = request.GET.get('msag_id')
    if not msag_id:
        return JsonResponse({'ports': []})
    
    ports = DSLPort.objects.filter(msag_id=msag_id, status='Available').values('id', 'port_number')
    return JsonResponse({'ports': list(ports)})



from django.http import JsonResponse
from .models import DSLPort

def get_ports_for_card(request):
    dsl_card_id = request.GET.get('dsl_card')
    if not dsl_card_id:
        return JsonResponse([], safe=False)

    ports = DSLPort.objects.filter(dsl_card_id=dsl_card_id, status=False, customer__isnull=True)
    ports_data = [{'id': port.id, 'port_number': port.port_number} for port in ports]
    return JsonResponse(ports_data, safe=False)







from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DSLPort, DSLCard
from .serializers import DSLPortSerializer

class AvailablePortsView(APIView):
    def get(self, request, card_id):
        try:
            dsl_card = DSLCard.objects.get(pk=card_id)
            available_ports = DSLPort.objects.filter(dsl_card=dsl_card, status=False, customer__isnull=True)
            serializer = DSLPortSerializer(available_ports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DSLCard.DoesNotExist:
            return Response({'error': 'DSL Card not found'}, status=status.HTTP_404_NOT_FOUND)



from django.http import JsonResponse
from .utils import send_email

def send_email_view(request):
    if request.method == "POST":
        subject = "Your Receipt is Ready"
        message = "Thank you for using our service. Attached is your receipt."
        recipient_list = ["recipient@example.com"]  # Replace with dynamic recipient
        try:
            send_email(subject, message, recipient_list)
            return JsonResponse({"success": True, "message": "Email sent successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

from django.shortcuts import render
from django.db.models import Count, Q
from .models import Customer

def customer_list_view(request):
    customers = Customer.objects.all()
    
    # Calculate statistics
    total_customers = customers.count()
    total_ipv6_enabled = customers.filter(ipv6_enabled=True).count()
    total_dsl_enabled = customers.filter(dsl_enabled=True).count()
    
    # Group by MSAG
    msag_stats = customers.values('msag__name').annotate(
        total_customers=Count('id'),
        ipv6_enabled=Count('id', filter=Q(ipv6_enabled=True)),
        dsl_enabled=Count('id', filter=Q(dsl_enabled=True))
    )

    context = {
        'customers': customers,
        'statistics': {
            'total_customers': total_customers,
            'total_ipv6_enabled': total_ipv6_enabled,
            'total_dsl_enabled': total_dsl_enabled,
        },
        'msag_stats': msag_stats,
    }
    return render(request, 'customers.html', context)

