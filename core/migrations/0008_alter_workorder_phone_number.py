# Generated by Django 5.1.4 on 2025-01-08 07:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_workorder_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='phone_number',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='work_order', to='core.customer'),
            preserve_default=False,
        ),
    ]
