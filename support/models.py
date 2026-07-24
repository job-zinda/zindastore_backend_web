from django.db import models
from django.utils import timezone
from orders.models import Order, OrderItem


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ReturnRequest(TimeStampedModel):
    STATUS_REQUESTED = "requested"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_RECEIVED = "received"
    STATUS_REFUNDED = "refunded"
    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_RECEIVED, "Received"),
        (STATUS_REFUNDED, "Refunded"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="returns")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="returns")
    reason = models.CharField(max_length=240)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"RMA {self.order.order_number} - {self.order_item.sku_snapshot}"

# Create your models here.
