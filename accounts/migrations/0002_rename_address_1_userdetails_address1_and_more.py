# Generated by Django 5.0.6 on 2024-06-01 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userdetails',
            old_name='address_1',
            new_name='address1',
        ),
        migrations.RemoveField(
            model_name='userdetails',
            name='address_2',
        ),
        migrations.AddField(
            model_name='userdetails',
            name='address2',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
