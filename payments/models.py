from django.db import models
from django.utils import timezone
from orders.models import Order


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PaymentIntent(TimeStampedModel):
    PROVIDER_RAZORPAY = "razorpay"
    PROVIDER_STRIPE = "stripe"
    PROVIDER_CHOICES = [
        (PROVIDER_RAZORPAY, "Razorpay"),
        (PROVIDER_STRIPE, "Stripe"),
    ]

    STATUS_REQUIRES_ACTION = "requires_action"
    STATUS_PENDING = "pending"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_REQUIRES_ACTION, "Requires Action"),
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCEEDED, "Succeeded"),
        (STATUS_CANCELED, "Canceled"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payment_intents")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    client_secret = models.CharField(max_length=140, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payload = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.provider} intent for {self.order.order_number}"


class PaymentTransaction(TimeStampedModel):
    EVENT_AUTHORIZED = "authorized"
    EVENT_CAPTURED = "captured"
    EVENT_FAILED = "failed"
    EVENT_REFUNDED = "refunded"
    EVENT_CHOICES = [
        (EVENT_AUTHORIZED, "Authorized"),
        (EVENT_CAPTURED, "Captured"),
        (EVENT_FAILED, "Failed"),
        (EVENT_REFUNDED, "Refunded"),
    ]

    intent = models.ForeignKey(PaymentIntent, on_delete=models.CASCADE, related_name="transactions")
    provider_txn_id = models.CharField(max_length=140)
    event = models.CharField(max_length=20, choices=EVENT_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20)
    payload = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.event} {self.provider_txn_id}"


class Refund(TimeStampedModel):
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.CASCADE, related_name="refunds")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=140, blank=True)
    status = models.CharField(max_length=20, default="pending")
    provider_ref = models.CharField(max_length=140, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Refund {self.amount} for {self.transaction.provider_txn_id}"

# Create your models here.
