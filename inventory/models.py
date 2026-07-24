from django.db import models
from catalog.models import ProductVariant


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Warehouse(TimeStampedModel):
    name = models.CharField(max_length=140)
    code = models.CharField(max_length=40, unique=True)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class InventoryItem(TimeStampedModel):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="inventory")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="inventory")
    on_hand = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=0)

    class Meta:
        unique_together = ("variant", "warehouse")

    def __str__(self):
        return f"{self.variant.sku} @ {self.warehouse.code}"


class StockMovement(TimeStampedModel):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    ADJUSTMENT = "adjustment"
    RESERVATION = "reservation"
    TYPE_CHOICES = [
        (INBOUND, "Inbound"),
        (OUTBOUND, "Outbound"),
        (ADJUSTMENT, "Adjustment"),
        (RESERVATION, "Reservation"),
    ]

    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=140, blank=True)
    note = models.CharField(max_length=240, blank=True)

    def __str__(self):
        return f"{self.type} {self.quantity} {self.variant.sku}"

# Create your models here.
