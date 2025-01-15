from rest_framework import serializers
from .models import DSLPort

class DSLPortSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSLPort
        fields = ['id', 'port_number', 'status']
