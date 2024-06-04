# Generated by Django 5.0.6 on 2024-05-31 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0002_returnrequest_price_refund'),
    ]

    operations = [
        migrations.AlterField(
            model_name='returnrequest',
            name='price_refund',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
