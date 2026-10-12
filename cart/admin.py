from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Cart, CartItem


class CartItemInline(TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("variant", "quantity", "unit_price_snapshot", "total_price_snapshot")


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ("token", "status", "created_at", "updated_at")
    search_fields = ("token",)
    list_filter = ("status",)
    inlines = [CartItemInline]

# Register your models here.
