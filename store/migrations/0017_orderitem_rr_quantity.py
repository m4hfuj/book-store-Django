# Generated by Django 5.0.6 on 2024-06-01 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_itemtype_cartitem_type_orderitem_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='rr_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
