from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Brand(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(TimeStampedModel):
    TYPE_PRODUCT = "product"
    TYPE_SERVICE = "service"
    TYPE_COURSE = "course"
    TYPE_CHOICES = (
        (TYPE_PRODUCT, "Product"),
        (TYPE_SERVICE, "Service"),
        (TYPE_COURSE, "Course"),
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children"
    )
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_PRODUCT)

    class Meta:
        unique_together = ("parent", "name", "type")
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.parent.slug}-{self.name}" if self.parent else self.name
            self.slug = slugify(base)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"type": Category.TYPE_PRODUCT},
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    specs = models.JSONField(default=dict, blank=True)
    referral_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="E.g. 919999999999 without +")
    whatsapp_message = models.CharField(max_length=240, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.title}-{self.brand.name if self.brand else ''}".strip()
            self.slug = slugify(base)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Service(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.CharField(max_length=240, blank=True)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="services/", blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"type": Category.TYPE_SERVICE},
    )
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="E.g. 919999999999 without +")
    whatsapp_message = models.CharField(max_length=240, blank=True)
    is_active = models.BooleanField(default=True)
    referral_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=64, unique=True)
    variant_attributes = models.JSONField(default=dict, blank=True)
    mrp_price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percent
    is_active = models.BooleanField(default=True)
    weight_grams = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.title} [{self.sku}]"


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name="images", null=True, blank=True
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"Image for {self.product.title}"

class Course(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    author = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="courses/", blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"type": Category.TYPE_COURSE},
    )
    mrp_price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    referral_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="E.g. 919999999999 without +")
    whatsapp_message = models.CharField(max_length=240, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

