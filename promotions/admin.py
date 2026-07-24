from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "value", "is_active", "usage_count", "usage_limit")
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)

# Register your models here.
