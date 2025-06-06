from django.db import models
from . import constants
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import start_geocoding_thread

class Shipment(models.Model):
    sender_name = models.CharField(max_length=150)
    sender_email = models.EmailField()
    sender_phone = models.CharField(max_length=20)
    sender_address = models.CharField(max_length=200)

    receiver_name = models.CharField(max_length=150)
    receiver_email = models.EmailField()
    receiver_phone = models.CharField(max_length=20)
    receiver_address = models.CharField(max_length=200)

    tracking_number = models.CharField(max_length=100, unique=True)
    weight = models.CharField(max_length=50)
    content = models.CharField(max_length=400)
    shipping_type = models.CharField(max_length=100)
    origin_office = models.CharField(max_length=100)
    destination_office = models.CharField(max_length=100)
    shipping_date = models.DateField()
    delivery_date = models.DateField()
    booking_mode = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.sender_name


class LiveUpdate(models.Model):
    shipment = models.ForeignKey(Shipment, related_name='live_update', on_delete=models.CASCADE)
    current_location = models.CharField(max_length=150)
    status = models.CharField(max_length=150)
    remark = models.CharField(max_length=500, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    stages_status = models.CharField(max_length=50, choices=constants.STATES_LIVE_CHOICES)
    stages_label = models.CharField(max_length=50, choices=constants.STATES_LABEL_CHOICES)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if (self.latitude is None or self.longitude is None) and self.current_location:
            start_geocoding_thread(self.id)

    def __str__(self):
        return self.status
    

class CountryLocation(models.Model):
    country_name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def save(self, *args, **kwargs):
        # Normalize country_name to title case (e.g., "france" -> "France")
        self.country_name = self.country_name.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.country_name


class MessageLog(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('QUEUED', 'Queued'),
        ('SENDING', 'Sending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('UNDELIVERED', 'Undelivered'),
        ('FAILED', 'Failed'),
        ('ERROR', 'Error'),
    ]

    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='sms_logs')
    to = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    sid = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SMS to {self.to} for Shipment #{self.shipment.id} [{self.status}]"