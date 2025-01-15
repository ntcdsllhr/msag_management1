"""
URL configuration for msag_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core.views import dashboard
from core.views import AvailablePortsView
# urls.py

from core.views import get_ports_for_card
from core.views import customer_list_view

from core import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Dashboard view
    path('new-connection/', views.new_connection_request, name='new_connection_request'),
    path('issue-modem/<int:request_id>/', views.issue_modem, name='issue_modem'),
    path('assign-technician/<int:work_order_id>/', views.assign_technician, name='assign_technician'),

    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('new-connection/', views.new_connection_request, name='new_connection_request'),
    path('issue-modem/<int:request_id>/', views.issue_modem, name='issue_modem'),
    path('assign-technician/<int:work_order_id>/', views.assign_technician, name='assign_technician'),
    path('comprehensive-report/', views.comprehensive_report, name='comprehensive_report'),
    path('generate-receipt/<int:work_order_id>/', views.generate_cpe_receipt, name='generate_cpe_receipt'),


    path('admin/get_available_ports/', views.get_available_ports, name='get_available_ports'),
    path('get_ports_for_card/', get_ports_for_card, name='get_ports_for_card'),
    path('api/dslcard/<int:card_id>/available-ports/', AvailablePortsView.as_view(), name='available_ports'),
    path('api/ports/<int:card_id>/', get_ports_for_card, name='get_ports_for_card'),
    path('send-email/', views.send_email_view, name='send_email'),
    path('customers/', customer_list_view, name='customer-list'),
    
]
