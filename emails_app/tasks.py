# emails/tasks.py

from celery import shared_task, chord, group
from celery.utils.log import get_task_logger
from django.core.mail import EmailMessage

from emails_app.utils import chunk_list
from .models import Client, EmailRecord, TaskTypeChoices


logger = get_task_logger(__name__)


@shared_task(bind=True)
def test_func(self):
    # operation
    for i in range(10):
        print(i)
    return 'Done'


@shared_task(bind=True)
def say_helo(self):
    print('Hello')
    return "Sayed Hello"


@shared_task(bind=True)
def send_email_task(self, subject, message, recipient, attachments=None, html_message=None, client_pk=None):
    from .models import Client
    try:
        client = Client.objects.get(pk=client_pk)
        email = EmailMessage(subject=subject, body=message, to=[recipient])
        if html_message:
            email.content_subtype = 'html'
            email.body = html_message
        # if attachments:
        #     for attachment in attachments:
        #         # Assume attachment is a file path, you can adjust based on actual data
        #         email.attach_file(attachment)

        if attachments:
            for attachment in attachments:
                file_name, file_content, content_type = attachment
                email.attach(file_name, file_content, content_type)

        email.send()

        # Save email record to database
        EmailRecord.objects.create(
            client=client, subject=subject, recipient=recipient, status='Sent', task_type=TaskTypeChoices.SINGLE
        )

        return True
    except Exception as e:
        # Log the error and retry the task if an exception occurs
        self.retry(exc=e, countdown=60, max_retries=3)
        EmailRecord.objects.create(
            client=client, subject=subject, recipient=recipient, status='Failed', error_message=str(e), task_type=TaskTypeChoices.SINGLE
        )
        return False


@shared_task(bind=True)
def send_bulk_email_task(self, subject, message, recipient_list, attachments_list=None, html_message=None, client_pk=None, collective=False):
    try:
        client = Client.objects.get(pk=client_pk)

        if collective:
            # Send collectively to all recipients
            email = EmailMessage(subject, message, to=recipient_list)
            if html_message:
                email.content_subtype = 'html'
                email.body = html_message

            if attachments_list:
                for attachment in attachments_list:
                    file_name, file_content, content_type = attachment
                    email.attach(file_name, file_content, content_type)

            email.send()

            # Save one email record for the collective sending
            EmailRecord.objects.create(
                client=client, subject=subject, recipient=', '.join(recipient_list), status='Sent', task_type=TaskTypeChoices.BULK
            )
        else:
            # Send individually to each recipient
            # Chunk the recipient list for individual sending
            chunk_size = 2  # Adjust the chunk size based on your requirements
            recipient_chunks = list(chunk_list(recipient_list, chunk_size))

            # Create subtasks for each chunk using group
            tasks = group(send_email_chunk.s(subject, message, chunk, attachments_list,
                          html_message, client_pk) for chunk in recipient_chunks)

            # Use chord to execute tasks in parallel and handle the final result
            result = chord(tasks)(
                finalize_send_bulk_email.s(client_pk, subject))

        return True
    except Exception as e:
        # Log the error and retry the task if an exception occurs
        logger.error(f"Error sending bulk email: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=3)
        if collective:
            EmailRecord.objects.create(
                client=client, subject=subject, recipient=', '.join(recipient_list), status='Failed', error_message=str(e), task_type=TaskTypeChoices.BULK
            )
        else:
            for recipient in recipient_list:
                EmailRecord.objects.create(
                    client=client, subject=subject, recipient=recipient, status='Failed', error_message=str(e), task_type=TaskTypeChoices.BULK
                )
        return False


@shared_task(bind=True)
def send_email_chunk(self, subject, message, recipient_chunk, attachments_list, html_message, client_pk):
    try:
        client = Client.objects.get(pk=client_pk)
        for recipient in recipient_chunk:
            email = EmailMessage(subject, message, to=[recipient])
            if html_message:
                email.content_subtype = 'html'
                email.body = html_message

            if attachments_list:
                for attachment in attachments_list:
                    file_name, file_content, content_type = attachment
                    email.attach(file_name, file_content, content_type)

            email.send()

            # Save email record to database for each recipient
            EmailRecord.objects.create(
                client=client, subject=subject, recipient=recipient, status='Sent', task_type=TaskTypeChoices.BULK
            )

        return True
    except Exception as e:
        # Log the error
        logger.error(f"Error sending email chunk: {str(e)}")
        for recipient in recipient_chunk:
            EmailRecord.objects.create(
                client=client, subject=subject, recipient=recipient, status='Failed', error_message=str(e), task_type=TaskTypeChoices.BULK
            )
        return False


@shared_task(bind=True)
def finalize_send_bulk_email(self, results, client_pk, subject):
    # This function runs after all chunks have been processed
    logger.info(
        f"Finished sending bulk email for client {client_pk} with subject {subject}")
    return True
