from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

class Event(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    event_date = models.DateField()

class EmailTemplate(models.Model):
    event_type = models.CharField(max_length=50, unique=True)
    template = models.TextField()

class EmailLog(models.Model):
    email_to = models.EmailField()
    event_type = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=[('Success', 'Success'), ('Error', 'Error')])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email_to} - {self.event_type} - {self.status}"



# Create your models here.
