from django.db import models
from catalog.models import Product


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Review(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1-5
    title = models.CharField(max_length=140, blank=True)
    body = models.TextField(blank=True)
    name_or_email = models.CharField(max_length=140, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.title} - {self.rating}★"

# Create your models here.
