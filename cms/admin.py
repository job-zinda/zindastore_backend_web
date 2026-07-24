from django.contrib import admin
from django import forms

from .models import Banner, Page
from catalog.models import Brand, Category, Product


from dal import autocomplete


class BannerLinkBuilderForm(forms.ModelForm):
    DEST_PRODUCTS_ALL = "products_all"
    DEST_PRODUCTS_BRAND = "products_brand"
    DEST_PRODUCTS_CATEGORY = "products_category"
    DEST_PRODUCT_DETAIL = "product_detail"
    DEST_CATEGORIES = "categories"
    DEST_BRANDS = "brands"
    DEST_CART = "cart"
    DEST_CHECKOUT = "checkout"
    DEST_PRODUCTS_SEARCH = "products_search"

    LINK_DEST_CHOICES = (
        (DEST_PRODUCTS_ALL, "Products - All"),
        (DEST_PRODUCTS_BRAND, "Products - By Brand"),
        (DEST_PRODUCTS_CATEGORY, "Products - By Category"),
        (DEST_PRODUCTS_SEARCH, "Products - Search Query"),
        (DEST_PRODUCT_DETAIL, "Product Detail"),
        (DEST_CATEGORIES, "Categories"),
        (DEST_BRANDS, "Brands"),
        (DEST_CART, "Cart"),
        (DEST_CHECKOUT, "Checkout"),
    )

    # Builder helper fields (not stored on model)
    # Option B: unified searchable dropdown (preferred)
    link_path_auto = forms.CharField(
        label="Link (search brands/categories/products or choose static)",
        required=False,
        widget=autocomplete.ListSelect2(url="cms-banner-link-autocomplete"),
        help_text="Search and select a destination. This will write into link_path.",
    )
    # Hide legacy preset fields (kept for backward compat, but not shown)
    link_destination = forms.ChoiceField(
        choices=LINK_DEST_CHOICES,
        required=False,
        widget=forms.HiddenInput,
    )
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=False, widget=forms.HiddenInput)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, widget=forms.HiddenInput)
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False, widget=forms.HiddenInput)
    search_query = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Banner
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        # If unified dropdown used, prioritize it
        link_path_auto = cleaned.get("link_path_auto")
        if link_path_auto:
            cleaned["link_path"] = link_path_auto
            return cleaned

        # Legacy presets are hidden; if someone submits them programmatically,
        # we ignore them by default to avoid accidental overrides.
        return cleaned


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    form = BannerLinkBuilderForm
    list_display = ("title", "placement", "is_active", "sort_order", "updated_at", "link_path", "link_url")
    list_filter = ("placement", "is_active")
    search_fields = ("title", "link_path")

    actions = [
        "set_link_products_all",
        "set_link_categories", 
        "set_link_brands",
        "set_link_cart",
        "set_link_checkout",
        "clear_links",
    ]

    @admin.action(description="Set link_path = /products")
    def set_link_products_all(self, request, queryset):
        queryset.update(link_path="/products")

    @admin.action(description="Set link_path = /categories")
    def set_link_categories(self, request, queryset):
        queryset.update(link_path="/categories")

    @admin.action(description="Set link_path = /brands")
    def set_link_brands(self, request, queryset):
        queryset.update(link_path="/brands")

    @admin.action(description="Set link_path = /cart")
    def set_link_cart(self, request, queryset):
        queryset.update(link_path="/cart")

    @admin.action(description="Set link_path = /checkout")
    def set_link_checkout(self, request, queryset):
        queryset.update(link_path="/checkout")

    @admin.action(description="Clear link_path and link_url")
    def clear_links(self, request, queryset):
        queryset.update(link_path="", link_url="")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("slug", "title")

# Register your models here.
