from django.db import models
from django.utils import timezone
from catalog.models import Product, ProductVariant
from cart.models import Cart


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Order(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELED = "canceled"
    STATUS_RETURNED = "returned"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELED, "Canceled"),
        (STATUS_RETURNED, "Returned"),
    ]

    PAYMENT_PENDING = "pending"
    PAYMENT_PAID = "paid"
    PAYMENT_FAILED = "failed"
    PAYMENT_REFUNDED = "refunded"
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_PAID, "Paid"),
        (PAYMENT_FAILED, "Failed"),
        (PAYMENT_REFUNDED, "Refunded"),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="INR")

    # Guest customer snapshot
    customer_name = models.CharField(max_length=140)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)

    # Address snapshots
    shipping_address = models.JSONField(default=dict)
    billing_address = models.JSONField(default=dict)

    placed_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True)

    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    # Referral info
    referral_code = models.CharField(max_length=40, blank=True)
    referral_credited = models.BooleanField(default=False)

    def __str__(self):
        return self.order_number


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    title_snapshot = models.CharField(max_length=220)
    sku_snapshot = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField()
    unit_price_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    total_price_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate_snapshot = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.order.order_number} - {self.sku_snapshot}"


class Invoice(TimeStampedModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=20, unique=True)
    issued_at = models.DateTimeField(default=timezone.now)
    pdf = models.FileField(upload_to="invoices/", blank=True, null=True)

    def __str__(self):
        return self.invoice_number

# Create your models here.
