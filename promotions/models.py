from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Coupon(TimeStampedModel):
    TYPE_AMOUNT = "amount"
    TYPE_PERCENT = "percent"
    DISCOUNT_TYPE_CHOICES = [
        (TYPE_AMOUNT, "Amount"),
        (TYPE_PERCENT, "Percent"),
    ]

    code = models.CharField(max_length=40, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    usage_limit = models.IntegerField(default=0)  # 0 = unlimited
    usage_count = models.IntegerField(default=0)
    min_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def is_valid_now(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_at and now < self.start_at:
            return False
        if self.end_at and now > self.end_at:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True

    def __str__(self):
        return self.code

# Create your models here.
