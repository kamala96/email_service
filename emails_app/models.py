
from django.core.exceptions import ValidationError
from django.db import models

from django.contrib.auth.models import User

from django.utils.translation import gettext_lazy as _


class TaskTypeChoices(models.TextChoices):
    SINGLE = 'single', _('Single Email')
    BULK = 'bulk', _('Bulk Email')


class SMTPSettings(models.Model):
    host = models.CharField(
        max_length=255,
        verbose_name="SMTP Host",
        help_text="The SMTP server address. For example, 'smtp.gmail.com'."
    )
    port = models.PositiveIntegerField(
        verbose_name="SMTP Port",
        help_text="The port to use for the SMTP server. Common ports are 587 for TLS or 465 for SSL."
    )
    username = models.CharField(
        max_length=255,
        verbose_name="SMTP Username",
        help_text="The username for authenticating with the SMTP server."
    )
    password = models.CharField(
        max_length=255,
        verbose_name="SMTP Password",
        help_text="The password for authenticating with the SMTP server. Ensure this is stored securely."
    )
    use_tls = models.BooleanField(
        default=True,
        verbose_name="Use TLS",
        help_text="Whether to use TLS (Transport Layer Security) when connecting to the SMTP server."
    )
    use_ssl = models.BooleanField(
        default=False,
        verbose_name="Use SSL",
        help_text="Whether to use SSL (Secure Sockets Layer) when connecting to the SMTP server. Note: Do not enable both TLS and SSL."
    )
    default_from_email = models.EmailField(
        verbose_name="Default From Email",
        help_text="The default email address to use for the 'From' field when sending emails."
    )

    class Meta:
        verbose_name = "SMTP Setting"
        verbose_name_plural = "SMTP Settings"

    def clean(self):
        if self.use_tls and self.use_ssl:
            raise ValidationError("Do not enable both TLS and SSL.")
        super(SMTPSettings, self).clean()

    def save(self, *args, **kwargs):
        if self.use_ssl:
            self.port = 465
        elif self.use_tls:
            self.port = 587
        else:
            self.port = 25  # Default SMTP port if neither TLS nor SSL is used
        super(SMTPSettings, self).save(*args, **kwargs)

    def __str__(self):
        return f"SMTP Settings for {self.host}"

# Optionally, you can add a method to retrieve the SMTP settings from the database


def get_smtp_settings():
    try:
        return SMTPSettings.objects.get()
    except SMTPSettings.DoesNotExist:
        return None


class Client(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name="Related User", blank=True, null=True
    )
    system_name = models.CharField(
        max_length=100, verbose_name="System Name", help_text="Name of the client system"
    )
    static_ip = models.GenericIPAddressField(
        verbose_name="Static IP", unique=True, help_text="Static IP address of the client system"
    )

    def __str__(self):
        return f"{self.system_name} ({self.static_ip})"

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"


class EmailRecord(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='email_records',
        verbose_name="Client",
        help_text="The client associated with this email record."
    )
    subject = models.CharField(
        max_length=255,
        verbose_name="Subject",
        help_text="The subject of the email."
    )
    recipient = models.EmailField(
        verbose_name="Recipient",
        help_text="The email address of the recipient."
    )
    status = models.CharField(
        max_length=10,
        verbose_name="Status",
        help_text="The status of the email (e.g., 'Sent', 'Failed')."
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Error Message",
        help_text="The error message if the email sending failed."
    )
    task_type = models.CharField(
        max_length=20,
        choices=TaskTypeChoices.choices,
        default=TaskTypeChoices.SINGLE,
        verbose_name="Task Type",
        help_text="The type of task used to send the email (single or bulk)."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp",
        help_text="The date and time when the email record was created."
    )

    def __str__(self):
        return f'{self.subject} to {self.recipient} - {self.status}'

    class Meta:
        verbose_name = "Email Record"
        verbose_name_plural = "Email Records"
