from django.contrib import admin
from .models import Service, Brand, Category, Product, ProductVariant, ProductImage, Course


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
  list_display = ("title", "is_active", "base_price", "updated_at")
  search_fields = ("title", "summary")
  list_filter = ("is_active",)

from django.contrib import admin
from .models import Brand, Category, Product, ProductVariant, ProductImage, Course
from .forms import ProductAdminForm


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("sku", "sale_price", "mrp_price", "is_active")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "parent", "is_active", "updated_at")
    list_filter = ("type", "is_active", "parent")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "brand", "category", "is_active", "updated_at")
    list_filter = ("brand", "category", "is_active")
    search_fields = ("title", "brand__name", "category__name")
    inlines = [ProductVariantInline, ProductImageInline]
    prepopulated_fields = {"slug": ("title",)}
    form = ProductAdminForm


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "sale_price", "mrp_price", "is_active", "updated_at")
    list_filter = ("is_active", "product__brand", "product__category")
    search_fields = ("sku", "product__title")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "variant", "sort_order")
    list_filter = ("product",)

# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "sale_price", "mrp_price", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "author")
    prepopulated_fields = {"slug": ("title",)}
