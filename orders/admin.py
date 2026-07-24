from django.contrib import admin
from .models import Order, OrderItem, Invoice


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("title_snapshot", "sku_snapshot", "quantity", "unit_price_snapshot", "total_price_snapshot")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "status", "payment_status", "grand_total", "created_at")
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("order_number", "customer_name", "customer_email", "customer_phone")
    inlines = [OrderItemInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "order", "issued_at")
    search_fields = ("invoice_number", "order__order_number")

# Register your models here.
