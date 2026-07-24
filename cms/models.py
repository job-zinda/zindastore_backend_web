from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Banner(TimeStampedModel):
    PLACEMENT_CHOICES = [
        ("home_top", "Home - Top"),
        ("home_mid", "Home - Middle"),
        ("home_bottom", "Home - Bottom"),
    ]

    title = models.CharField(max_length=140)
    image = models.ImageField(upload_to="banners/")
    link_url = models.URLField(blank=True)
    # Optional relative path to support in-app navigation (e.g., "/products?brand=abc")
    link_path = models.CharField(max_length=200, blank=True)
    placement = models.CharField(max_length=40, choices=PLACEMENT_CHOICES, default="home_top")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.title


class Page(TimeStampedModel):
    slug = models.SlugField(max_length=140, unique=True)
    title = models.CharField(max_length=140)
    body = models.TextField()
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

# Create your models here.
