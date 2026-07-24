from django.contrib import admin
from .models import Warehouse, InventoryItem, StockMovement


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "city", "state", "is_active", "updated_at")
    search_fields = ("name", "code", "city", "state")
    list_filter = ("is_active",)


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("variant", "warehouse", "on_hand", "reserved", "updated_at")
    list_filter = ("warehouse",)
    search_fields = ("variant__sku", "warehouse__code")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("type", "variant", "warehouse", "quantity", "created_at")
    list_filter = ("type", "warehouse")
    search_fields = ("variant__sku", "reference")

# Register your models here.
