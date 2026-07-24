from django.db import models
from django.utils import timezone
from orders.models import Order, OrderItem


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ShippingMethod(TimeStampedModel):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=40, unique=True)
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rules = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Shipment(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_PACKED = "packed"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_RETURNED = "returned"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PACKED, "Packed"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_RETURNED, "Returned"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipments")
    method = models.ForeignKey(ShippingMethod, on_delete=models.SET_NULL, null=True, blank=True)
    carrier = models.CharField(max_length=120, blank=True)
    tracking_number = models.CharField(max_length=140, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Shipment for {self.order.order_number}"


class ShipmentItem(TimeStampedModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="items")
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order_item.sku_snapshot} x {self.quantity}"

# Create your models here.
