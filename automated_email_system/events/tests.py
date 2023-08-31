from django.test import TestCase
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from .models import Event, EmailTemplate, Employee, EmailLog
from unittest.mock import patch

class SendEventEmailsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_send_emails_no_events(self):
        response = self.client.get(reverse('send-event-emails'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'No events scheduled for today.')

        self.assertEqual(EmailLog.objects.count(), 1)
        email_log = EmailLog.objects.first()
        self.assertEqual(email_log.email_to, 'N/A')
        self.assertEqual(email_log.event_type, 'No events scheduled')
        self.assertEqual(email_log.status, 'Info')

    @patch('django.core.mail.send_mail')
    def test_send_emails_with_events(self, mock_send_mail):
        # Create an Event for testing
        event = Event.objects.create(
            event_type='Conference',
            event_date=timezone.now().date(),
            sent_email=False,
            processed=False,
        )

        # Create an EmailTemplate for the event type
        email_template = EmailTemplate.objects.create(
            event_type='Conference',
            template='Hello {employee_name}, there is a {event_type} on {event_date}.'
        )

        # Create an Employee associated with the event
        employee = Employee.objects.create(
            name='John Doe',
            email='john@example.com',
        )
        employee.event.add(event)

        response = self.client.get(reverse('send-event-emails'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Event emails sent successfully')

        # Check that an EmailLog entry was created
        self.assertEqual(EmailLog.objects.count(), 1)
        email_log = EmailLog.objects.first()
        self.assertEqual(email_log.email_to, 'john@example.com')
        self.assertEqual(email_log.event_type, 'Conference')
        self.assertEqual(email_log.status, 'Success')

        # Check that the Event's status was updated
        event.refresh_from_db()
        self.assertTrue(event.sent_email)
        self.assertTrue(event.processed)

        # Check that the email was sent
        mock_send_mail.assert_called_once()

    @patch('django.core.mail.send_mail', side_effect=Exception('Email sending failed'))
    def test_email_sending_error(self, mock_send_mail):
        # Create an Event for testing
        event = Event.objects.create(
            event_type='Conference',
            event_date=timezone.now().date(),
            sent_email=False,
            processed=False,
        )

        # Create an EmailTemplate for the event type
        email_template = EmailTemplate.objects.create(
            event_type='Conference',
            template='Hello {employee_name}, there is a {event_type} on {event_date}.'
        )

        # Create an Employee associated with the event
        employee = Employee.objects.create(
            name='Jane Smith',
            email='jane@example.com',
        )
        employee.event.add(event)

        response = self.client.get(reverse('send-event-emails'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Event emails sent successfully')

        # Check that an EmailLog entry was created for the error
        self.assertEqual(EmailLog.objects.count(), 1)
        email_log = EmailLog.objects.first()
        self.assertEqual(email_log.email_to, 'jane@example.com')
        self.assertEqual(email_log.event_type, 'Conference')
        self.assertEqual(email_log.status, 'Error')

        # Check that the Event's status was updated
        event.refresh_from_db()
        self.assertTrue(event.sent_email)
        self.assertTrue(event.processed)

        # Check that the email sending was attempted
        mock_send_mail.assert_called_once()



# Create your tests here.
