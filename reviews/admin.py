from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "rating", "name_or_email", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    search_fields = ("product__title", "name_or_email", "title", "body")

# Register your models here.
