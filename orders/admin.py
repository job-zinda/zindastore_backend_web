from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Order, OrderItem, Invoice


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("title_snapshot", "sku_snapshot", "quantity", "unit_price_snapshot", "total_price_snapshot")


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("order_number", "status", "payment_status", "grand_total", "created_at")
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("order_number", "customer_name", "customer_email", "customer_phone")
    inlines = [OrderItemInline]


@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = ("invoice_number", "order", "issued_at")
    search_fields = ("invoice_number", "order__order_number")

# Register your models here.
