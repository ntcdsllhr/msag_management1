# Generated by Django 5.1.4 on 2025-01-06 05:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_workorder_dsl_port_workorder_modem_workorder_msag_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dslcard',
            name='card_type',
            field=models.CharField(choices=[('ADSL', 'ADSL'), ('VDSL', 'VDSL')], default='ADSL', max_length=4),
        ),
    ]
