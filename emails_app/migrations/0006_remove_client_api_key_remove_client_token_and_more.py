# Generated by Django 5.0.6 on 2024-06-17 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails_app', '0005_alter_client_api_key_alter_client_token_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='api_key',
        ),
        migrations.RemoveField(
            model_name='client',
            name='token',
        ),
        migrations.RemoveField(
            model_name='client',
            name='token_expiry',
        ),
    ]