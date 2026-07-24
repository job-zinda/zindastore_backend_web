from django.contrib import admin
from .models import ReturnRequest


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("order", "order_item", "status", "refund_amount", "created_at")
    list_filter = ("status",)
    search_fields = ("order__order_number", "order_item__sku_snapshot")

# Register your models here.
