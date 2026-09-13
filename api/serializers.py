from rest_framework import serializers
from catalog.models import Brand, Category, Product, ProductVariant, ProductImage, Course, Service
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from reviews.models import Review


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "description", "logo", "is_active"]


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "is_active", "type"]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "sku",
            "variant_attributes",
            "mrp_price",
            "sale_price",
            "tax_rate",
            "is_active",
            "weight_grams",
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "sort_order", "variant"]


class ProductListSerializer(serializers.ModelSerializer):
    brand = serializers.SlugRelatedField(slug_field="name", read_only=True)
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    thumbnail = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()
    mrp_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "brand",
            "category",
            "is_active",
            "thumbnail",
            "sale_price",
            "mrp_price",
            "referral_commission",
        ]

    def get_thumbnail(self, obj):
        first_image = next(iter(obj.images.all()), None)
        if first_image and getattr(first_image.image, "url", None):
            return first_image.image.url
        return ""

    def get_sale_price(self, obj):
        prices = [v.sale_price for v in obj.variants.all() if getattr(v, "sale_price", None) is not None]
        return str(min(prices)) if prices else None

    def get_mrp_price(self, obj):
        prices = [v.mrp_price for v in obj.variants.all() if getattr(v, "mrp_price", None) is not None]
        return str(min(prices)) if prices else None


class ProductDetailSerializer(serializers.ModelSerializer):
    brand = serializers.SlugRelatedField(slug_field="name", read_only=True)
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "brand",
            "category",
            "description",
            "specs",
            "is_active",
            "variants",
            "images",
            "whatsapp_number",
            "whatsapp_message",
            "referral_commission",
        ]


class CourseListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    class Meta:
        model = Course
        fields = '__all__'

    def get_thumbnail(self, obj):
        if getattr(obj.thumbnail, "url", None):
            return obj.thumbnail.url
        return ""


class CourseDetailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    class Meta:
        model = Course
        fields = '__all__'

    def get_thumbnail(self, obj):
        if getattr(obj.thumbnail, "url", None):
            return obj.thumbnail.url
        return ""


class ServiceListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    class Meta:
        model = Service
        fields = '__all__'

    def get_thumbnail(self, obj):
        if getattr(obj.thumbnail, "url", None):
            return obj.thumbnail.url
        return ""


class ServiceDetailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    class Meta:
        model = Service
        fields = '__all__'

    def get_thumbnail(self, obj):
        if getattr(obj.thumbnail, "url", None):
            return obj.thumbnail.url
        return ""

# --- Cart Serializers ---

class CartItemSerializer(serializers.ModelSerializer):
    variant_sku = serializers.CharField(source="variant.sku", read_only=True)
    product_title = serializers.CharField(source="variant.product.title", read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "variant_sku",
            "product_title",
            "thumbnail",
            "quantity",
            "unit_price_snapshot",
            "total_price_snapshot",
        ]

    def get_thumbnail(self, obj):
        try:
            v_images = getattr(obj.variant, "images", None)
            if v_images is not None:
                v_first = next(iter(v_images.all()), None)
                if v_first and getattr(v_first.image, "url", None):
                    return v_first.image.url
        except Exception:
            pass
        try:
            p_images = getattr(obj.variant.product, "images", None)
            if p_images is not None:
                p_first = next(iter(p_images.all()), None)
                if p_first and getattr(p_first.image, "url", None):
                    return p_first.image.url
        except Exception:
            pass
        return ""


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["token", "status", "currency", "created_at", "updated_at", "items"]


class CartAddItemSerializer(serializers.Serializer):
    variant_sku = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)


class CartItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

# --- Checkout & Request Serializers ---

class AddressSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=140)
    phone = serializers.CharField(max_length=20)
    address_line1 = serializers.CharField(max_length=200)
    address_line2 = serializers.CharField(max_length=200, required=False, allow_blank=True)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=100)
    pincode = serializers.CharField(max_length=20)


class CheckoutRequestSerializer(serializers.Serializer):
    token = serializers.CharField()
    customer_name = serializers.CharField(max_length=140)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    customer_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    shipping_address = AddressSerializer()
    billing_address = AddressSerializer(required=False)
    shipping_method_code = serializers.CharField(max_length=40)
    coupon_code = serializers.CharField(max_length=40, required=False, allow_blank=True)


class RazorpayVerifySerializer(serializers.Serializer):
    order_number = serializers.CharField()
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()


class CourseCheckoutRequestSerializer(serializers.Serializer):
    course_slug = serializers.CharField()
    customer_name = serializers.CharField(max_length=140)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    customer_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    coupon_code = serializers.CharField(max_length=40, required=False, allow_blank=True)


class ServiceCheckoutRequestSerializer(serializers.Serializer):
    service_slug = serializers.CharField()
    customer_name = serializers.CharField(max_length=140)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    customer_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    coupon_code = serializers.CharField(max_length=40, required=False, allow_blank=True)

# --- Review Serializers ---

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "title",
            "body",
            "name_or_email",
            "created_at",
        ]


class ReviewCreateSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    title = serializers.CharField(max_length=140, required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)
    name_or_email = serializers.CharField(max_length=140, required=False, allow_blank=True)
    
class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="title_snapshot")
    type = serializers.SerializerMethodField() # product / course / service
    price = serializers.DecimalField(source="unit_price_snapshot", max_digits=12, decimal_places=2)
    total = serializers.DecimalField(source="total_price_snapshot", max_digits=12, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = [
            "id", 
            "name", 
            "type", 
            "sku_snapshot", 
            "quantity", 
            "price", 
            "total"
        ]

    def get_type(self, obj):
        if obj.product:
            return "product"
        if obj.course:
            return "course"
        if obj.service:
            return "service"
        return "other"

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(source="grand_total", max_digits=12, decimal_places=2)
    created_at = serializers.DateTimeField(source="placed_at")
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField()

    class Meta:
        model = Order
        fields = [
            "id", 
            "order_number", 
            "status", 
            "payment_status",
            "created_at", 
            "total_amount",
            "currency",
            "customer_name",
            "customer_email",
            "customer_phone",
            "items",
        ]


