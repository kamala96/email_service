# Generated by Django 5.0.6 on 2024-06-17 12:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails_app', '0002_emailrecord_error_message_alter_emailrecord_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_name', models.CharField(help_text='Name of the client system', max_length=100, verbose_name='System Name')),
                ('static_ip', models.GenericIPAddressField(help_text='Static IP address of the client system', verbose_name='Static IP')),
                ('api_key', models.CharField(help_text='Unique API key for client', max_length=100, unique=True, verbose_name='API Key')),
                ('token', models.CharField(max_length=255, verbose_name='Access Token')),
                ('token_expiry', models.DateTimeField(help_text='Expiration date and time of the access token', verbose_name='Token Expiry')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Related User')),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
            },
        ),
    ]