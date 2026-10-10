from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("target_item", "rating", "name_or_email", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    search_fields = ("product__title", "course__title", "service__title", "name_or_email", "title", "body")

    def target_item(self, obj):
        return obj.product or obj.course or obj.service or "N/A"
    target_item.short_description = "Item"

# Register your models here.
