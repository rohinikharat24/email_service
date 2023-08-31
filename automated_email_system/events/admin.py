from django.contrib import admin
from .models import Employee, Event, EmailTemplate, EmailLog

admin.site.register(Employee)
admin.site.register(Event)
admin.site.register(EmailTemplate)
admin.site.register(EmailLog)


# Register your models here.
