from django.db import models

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
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return self.sender_name


class LiveUpdate(models.Model):
    current_location = models.CharField(max_length=150)
    status = models.CharField(max_length=150)
    remark = models.CharField(max_length=500, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.status
