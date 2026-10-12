from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import PaymentIntent, PaymentTransaction, Refund


class PaymentTransactionInline(TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = ("provider_txn_id", "event", "amount", "status", "occurred_at")


@admin.register(PaymentIntent)
class PaymentIntentAdmin(ModelAdmin):
    list_display = ("order", "provider", "amount", "currency", "status", "created_at")
    list_filter = ("provider", "status", "currency")
    search_fields = ("order__order_number",)
    inlines = [PaymentTransactionInline]


@admin.register(Refund)
class RefundAdmin(ModelAdmin):
    list_display = ("transaction", "amount", "status", "created_at")
    list_filter = ("status",)

# Register your models here.
