
import logging

import requests
from .models import SMTPSettings
from rest_framework.exceptions import ErrorDetail
import string
import secrets
from enum import Enum
from django.conf import settings

logger = logging.getLogger("emails_app")


def set_smtp_settings():
    try:
        smtp_settings = SMTPSettings.objects.get()
        settings.EMAIL_HOST = smtp_settings.host
        settings.EMAIL_PORT = smtp_settings.port
        settings.EMAIL_HOST_USER = smtp_settings.username
        settings.EMAIL_HOST_PASSWORD = smtp_settings.password
        settings.EMAIL_USE_TLS = smtp_settings.use_tls
        settings.EMAIL_USE_SSL = smtp_settings.use_ssl
        settings.DEFAULT_FROM_EMAIL = smtp_settings.default_from_email
    except SMTPSettings.DoesNotExist:
        pass  # Handle the case where no SMTP settings are found
    except Exception:
        pass


# logger = logging.getLogger(__name__)


# def set_smtp_settings():
#     try:
#         smtp_settings = SMTPSettings.objects.get()

#         settings.EMAIL_HOST = smtp_settings.host
#         settings.EMAIL_PORT = smtp_settings.port
#         settings.EMAIL_HOST_USER = smtp_settings.username
#         settings.EMAIL_HOST_PASSWORD = smtp_settings.password
#         settings.EMAIL_USE_TLS = smtp_settings.use_tls
#         settings.EMAIL_USE_SSL = smtp_settings.use_ssl
#         settings.DEFAULT_FROM_EMAIL = smtp_settings.default_from_email

#         # Ensure only one of use_tls or use_ssl is enabled at a time
#         if smtp_settings.use_tls and smtp_settings.use_ssl:
#             logger.warning(
#                 "Both EMAIL_USE_TLS and EMAIL_USE_SSL are set to True. This might cause configuration issues.")

#         logger.info("SMTP settings successfully applied.")

#     except SMTPSettings.DoesNotExist:
#         logger.error(
#             "No SMTP settings found. Please configure the SMTP settings in the database.")
#     except Exception as e:
#         logger.exception(
#             "An unexpected error occurred while setting SMTP settings: %s", e)


def chunk_list(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def truncate_string(obj, field_name='description', max_length=60):
    """
    Truncates the specified field of the given object to a specified length.
    """
    field_value = getattr(
        obj, field_name, '')  # Get the value of the specified field
    if len(field_value) > max_length:
        return field_value[:max_length] + '...'
    return field_value


class ErrorCode(Enum):
    INVALID_IP = {'code': 1001, 'message': 'Invalid IP address'}
    INVALID_REQUEST = {'code': 1002, 'message': 'Invalid request data'}
    INTERNAL_ERROR = {'code': 1003, 'message': 'Internal server error'}
    # Add more error codes as needed

    def __str__(self):
        return self.name

    @property
    def code(self):
        return self.value['code']

    @property
    def message(self):
        return self.value['message']


def format_serializer_errors(serializer_errors):
    """
    Extracts and formats errors from the serializer into a structured dictionary,
    handling cases where errors may be lists, dictionaries, or strings.
    """
    error_details = {}

    for field, errors in serializer_errors.items():
        error_messages = []
        if isinstance(errors, dict):
            # Process dictionary of errors
            for key, error in errors.items():
                if isinstance(error, list):
                    for err in error:
                        if isinstance(err, ErrorDetail):
                            error_messages.append(f"{key}: {str(err)}")
                        else:
                            error_messages.append(f"{key}: {err}")
                elif isinstance(error, ErrorDetail):
                    error_messages.append(f"{key}: {str(error)}")
                else:
                    error_messages.append(f"{key}: {error}")
        elif isinstance(errors, list):
            # Process list of errors
            for error in errors:
                if isinstance(error, str):
                    error_messages.append(error)
                elif isinstance(error, dict):
                    for key, value in error.items():
                        if isinstance(value, list):
                            for val in value:
                                if isinstance(val, ErrorDetail):
                                    error_messages.append(f"{key}: {str(val)}")
                                else:
                                    error_messages.append(f"{key}: {val}")
                        elif isinstance(value, ErrorDetail):
                            error_messages.append(f"{key}: {str(value)}")
                        else:
                            error_messages.append(f"{key}: {value}")
                elif isinstance(error, ErrorDetail):
                    error_messages.append(str(error))
                else:
                    error_messages.append(str(error))
        elif isinstance(errors, ErrorDetail):
            # Process single ErrorDetail
            error_messages.append(str(errors))
        elif isinstance(errors, str):
            # Process single error string
            error_messages.append(errors)

        error_details[field] = error_messages

    return error_details


def generate_unique_api_key():
    # Generate a 32-character API key using random alphanumeric characters
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
    return api_key


def generate_unique_token():
    # Generate a 64-character token using random hexadecimal characters
    token = secrets.token_hex(32)
    return token


def get_server_ip(request):
    """
    Extracts the IP address of the server making the request.

    This function checks the `X-Forwarded-For` header first, which contains the original IP address 
    of the client making the request, as passed by proxies or load balancers. If the `X-Forwarded-For` 
    header is not present, it falls back to using the `REMOTE_ADDR` which is the IP address of the 
    immediate sender.

    Args:
        request (HttpRequest): The Django HTTP request object.

    Returns:
        str: The IP address of the server making the request.
    """
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Use the first IP address in the X-Forwarded-For list
            server_ip = x_forwarded_for.split(',')[0].strip()
        else:
            # Fallback to REMOTE_ADDR if X-Forwarded-For is not present
            server_ip = request.META.get('REMOTE_ADDR')

        return server_ip
    except requests.RequestException as e:
        logger.error(f"Error fetching public IP: {e}")
        return None


def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        data = response.json()
        return data.get('ip')
    except requests.RequestException as e:
        logger.error(f"Error fetching public IP: {e}")
        return None
