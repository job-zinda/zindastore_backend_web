from django.contrib import admin
from .models import ShippingMethod, Shipment, ShipmentItem


class ShipmentItemInline(admin.TabularInline):
    model = ShipmentItem
    extra = 0


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "base_rate", "is_active", "updated_at")
    search_fields = ("name", "code")
    list_filter = ("is_active",)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "carrier", "tracking_number", "created_at")
    list_filter = ("status", "carrier")
    search_fields = ("order__order_number", "tracking_number")
    inlines = [ShipmentItemInline]

# Register your models here.
