

from django.conf import settings
from django.utils import timezone
import jwt
from rest_framework.decorators import api_view, parser_classes, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta, datetime
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
import json
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from emails_app.models import Client
from emails_app.serializers import BulkEmailSerializer, EmailSerializer
from emails_app.utils import ErrorCode, format_serializer_errors
from .tasks import send_email_task, send_bulk_email_task, test_func

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import default_storage


def index(request):
    from django.http import HttpResponse
    return HttpResponse('Hi, Welcome to NIT Email Service (NES)')


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def send_single_email(request):
    serializer = EmailSerializer(data=request.data)
    client = get_object_or_404(Client, user=request.user)

    if serializer.is_valid():
        subject = serializer.validated_data['subject']
        message = serializer.validated_data.get('message', None)
        recipient = serializer.validated_data['recipient']
        # attachments = serializer.validated_data.get('attachments', [])
        attachments = request.FILES.getlist('attachments')
        html_message = serializer.validated_data.get('html_message', None)

        try:
            # Prepare attachments in a format suitable for EmailMessage
            attached_files = []
            for attachment in attachments:
                if isinstance(attachment, InMemoryUploadedFile):
                    # Handle in-memory file objects (BytesIO or similar)
                    file_name = attachment.name
                    file_content = attachment.read()
                    attached_files.append(
                        (file_name, file_content, attachment.content_type))
                else:
                    # Handle regular file objects (uploaded files saved on disk)
                    with open(attachment.temporary_file_path(), 'rb') as f:
                        attached_files.append(
                            (attachment.name, f.read(), attachment.content_type))

            # print(attached_files)

            # Call the Celery task to send the email
            send_email_task.delay(
                subject, message, recipient, attached_files, html_message, client.pk)
            success_response = {
                "success": True,
                'message': 'Email sending task has been initiated'
            }
            return Response(success_response, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            # Remember to Log the errors
            # print(str(e))
            error_response = {
                "success": False,
                'code': ErrorCode.INTERNAL_ERROR.code,
                'message': ErrorCode.INTERNAL_ERROR.message,
                'errors': []
            }
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        # print(serializer.errors)
        error_response = {
            "success": False,
            'code': ErrorCode.INVALID_REQUEST.code,
            'message': ErrorCode.INVALID_REQUEST.message,
            'errors': format_serializer_errors(serializer.errors)
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def send_bulk_email(request):
    serializer = BulkEmailSerializer(data=request.data)
    client = get_object_or_404(Client, user=request.user)

    if serializer.is_valid():
        subject = serializer.validated_data['subject']
        message = serializer.validated_data.get('message', None)
        recipient_list = serializer.validated_data['recipient_list']
        attachments = request.FILES.getlist('attachments')
        html_message = serializer.validated_data.get('html_message', None)
        collective = serializer.validated_data.get('collective', False)

        try:
            # Prepare attachments in a format suitable for EmailMessage
            attached_files = []
            for attachment in attachments:
                if isinstance(attachment, InMemoryUploadedFile):
                    # Handle in-memory file objects (BytesIO or similar)
                    file_name = attachment.name
                    file_content = attachment.read()
                    attached_files.append(
                        (file_name, file_content, attachment.content_type))
                else:
                    # Handle regular file objects (uploaded files saved on disk)
                    with open(attachment.temporary_file_path(), 'rb') as f:
                        attached_files.append(
                            (attachment.name, f.read(), attachment.content_type))

            # print(attached_files)

            # Call the Celery task to send the bulk emails
            send_bulk_email_task.delay(
                subject, message, recipient_list, attached_files, html_message, client.pk, collective=collective)

            success_response = {
                "success": True,
                'message': 'Bulky email sending task has been initiated'
            }
            return Response(success_response, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            error_response = {
                "success": False,
                'code': ErrorCode.INTERNAL_ERROR.code,
                'message': ErrorCode.INTERNAL_ERROR.message,
                'errors': []
            }
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        error_response = {
            "success": False,
            'code': ErrorCode.INVALID_REQUEST.code,
            'message': ErrorCode.INVALID_REQUEST.message,
            'errors': format_serializer_errors(serializer.errors)
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def obtain_token(request):
    static_ip = request.META.get(
        'HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

    try:
        client = Client.objects.get(static_ip=static_ip)
    except Client.DoesNotExist:
        error_response = {
            "success": False,
            'code': ErrorCode.INVALID_IP.code,
            'message': ErrorCode.INVALID_IP.message
        }
        return Response(error_response, status=status.HTTP_403_FORBIDDEN)

    try:
        # Generate a new refresh token
        refresh = RefreshToken.for_user(client.user)

        decoded_payload = jwt.decode(
            str(refresh.access_token), settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT["ALGORITHM"]])

        # Return the access and refresh tokens as JSON response
        return Response({
            "success": True,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'token_info': decoded_payload,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        error_response = {
            "success": False,
            'code': ErrorCode.INTERNAL_ERROR.code,
            'message': ErrorCode.INTERNAL_ERROR.message,
            'errors': str(e)
        }
        return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def test(request):
    test_func.delay()

    return Response('Done')


def schedule_mail(request):
    schedule, created = CrontabSchedule.objects.get_or_create(
        hour=1, minute=10)
    task = PeriodicTask.objects.create(
        crontab=schedule, name='schedule_task_unique', task='emails_app.tasks.say_helo', args=json.dumps(2, 3,))
    return Response('Schedule Done')

# # views.py
# def create_user(request):
#     # Note: simplified example, use a form to validate input
#     user = User.objects.create(username=request.POST['username'])
#     send_email.delay(user.pk)
#     return HttpResponse('User created')

# send_email.delay_on_commit(user.pk)

# # task.py
# @shared_task
# def send_email(user_pk):
#     user = User.objects.get(pk=user_pk)
#     # send email ...
