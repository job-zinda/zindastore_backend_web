from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("variant", "quantity", "unit_price_snapshot", "total_price_snapshot")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("token", "status", "created_at", "updated_at")
    search_fields = ("token",)
    list_filter = ("status",)
    inlines = [CartItemInline]

# Register your models here.
