from datetime import date
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Event, EmailTemplate, Employee, EmailLog
import logging
from django.utils import timezone
# from django_crontab import CronJobBase, Schedule

class SendEventEmails(APIView):
    def get(self, request):
        # Get the current date
        current_date = date.today()
        # Retrieve events scheduled for today
        events_today = Event.objects.filter(event_date=current_date)
         # Check if there are no events scheduled for today
        logger = logging.getLogger('no_events_logger')
        
        if not events_today:
            # logger = logging.getLogger('no_events_logger')
            logger.info("No events scheduled for today.")
            # Log the occurrence of no events
            EmailLog.objects.create(
                email_to='N/A',
                event_type='No events scheduled',
                status='Info',
                message='No events scheduled for today.',
            )
            return Response({"message": "No events scheduled for today."})

        # Create an empty list to store email content
        email_contents = []
        # Loop through events scheduled for today
        for event in events_today:
            try:
                email_template = EmailTemplate.objects.get(event_type=event.event_type)  # Fetch the corresponding email template for the event type
            except EmailTemplate.DoesNotExist:
                continue

            employees = Employee.objects.filter(event__id=event.id)     # Fetch employees associated with this event
           
            # Loop through employees and send emails
            for employee in employees:
                # Populate email template with employee and event details
                email_content = email_template.template.format(
                    employee_name=employee.name,
                    event_type=event.event_type,
                    event_date=event.event_date,
                )
                # Print the email content before sending
                logger.info(f"Email content for {employee.email}:\n{email_content}")
                retries = 0
                max_retries = 3
                while retries < max_retries:
                    try:
                        send_mail(
                            subject=f'Event: {event.event_type}',
                            message=email_content,
                            from_email='your@email.com',
                            recipient_list=[employee.email],
                        )
                        # Log successful email send
                        logger.info(f"Email sent to {employee.email} for event {event.event_type}")
                        EmailLog.objects.create(
                        email_to=employee.email,
                        event_type=event.event_type,
                        status='Success',
                        message=email_content,
                    )
                        break
                    except Exception as e:
                        # Log email sending error
                        logger.error(f"Error sending email to {employee.email} for event {event.event_type}: {str(e)}")
                        EmailLog.objects.create(
                            email_to=employee.email,
                            event_type=event.event_type,
                            status='Error',
                            message=str(e),
                    )
                    retries += 1
                else:
                    # Reached max retries, log the failure
                    logger.error(f"Failed to send email to {employee.email} for event {event.event_type} after {max_retries} retries.")        
                # Update event status to indicate email sent
                event.sent_email = True
                event.save()
            # Append the event's email content list to the main email contents list
            email_contents.append({"event_type": event.event_type, "email_content": email_content})

            # Update event status to indicate processing completion
            event.processed = True
            event.save()

        return Response({"message": "Event emails sent successfully", "email_contents": email_contents})



