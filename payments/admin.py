from django.contrib import admin
from .models import PaymentIntent, PaymentTransaction, Refund


class PaymentTransactionInline(admin.TabularInline):
    model = PaymentTransaction
    extra = 0
    readonly_fields = ("provider_txn_id", "event", "amount", "status", "occurred_at")


@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = ("order", "provider", "amount", "currency", "status", "created_at")
    list_filter = ("provider", "status", "currency")
    search_fields = ("order__order_number",)
    inlines = [PaymentTransactionInline]


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("transaction", "amount", "status", "created_at")
    list_filter = ("status",)

# Register your models here.
