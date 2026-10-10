from django.db import models
from catalog.models import Product, Course, Service


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Review(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    rating = models.PositiveSmallIntegerField()  # 1-5
    title = models.CharField(max_length=140, blank=True)
    body = models.TextField(blank=True)
    name_or_email = models.CharField(max_length=140, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        target = self.product or self.course or self.service or "Item"
        title = getattr(target, "title", str(target))
        return f"{title} - {self.rating}★"
