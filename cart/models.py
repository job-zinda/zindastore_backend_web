from django.db import models
from django.utils.crypto import get_random_string
from catalog.models import ProductVariant


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Cart(TimeStampedModel):
    STATUS_ACTIVE = "active"
    STATUS_CONVERTED = "converted"
    STATUS_ABANDONED = "abandoned"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_CONVERTED, "Converted"),
        (STATUS_ABANDONED, "Abandoned"),
    ]

    token = models.CharField(max_length=64, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    currency = models.CharField(max_length=3, default="INR")

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart {self.token[:8]}... ({self.status})"


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    total_price_snapshot = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("cart", "variant")

    def __str__(self):
        return f"{self.variant.sku} x {self.quantity}"

# Create your models here.
