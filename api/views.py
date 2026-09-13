import logging
from decimal import Decimal
import razorpay
from django.conf import settings
from django.db.models import F, Q, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Brand, Category, Product, ProductVariant, Course, Service
from cart.models import Cart, CartItem
from promotions.models import Coupon
from shipping.models import ShippingMethod
from orders.models import Order, OrderItem
from payments.models import PaymentIntent, PaymentTransaction
from reviews.models import Review

from .serializers import (
    BrandSerializer,
    CategorySerializer,
    OrderSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    CourseListSerializer,
    CourseDetailSerializer,
    ServiceListSerializer,
    ServiceDetailSerializer,
    CartSerializer,
    CartAddItemSerializer,
    CartItemUpdateSerializer,
    CheckoutRequestSerializer,
    CourseCheckoutRequestSerializer,
    ServiceCheckoutRequestSerializer,
    RazorpayVerifySerializer,
    ReviewSerializer,
    ReviewCreateSerializer,
)

# --- Catalog Views ---

class BrandList(APIView):
    def get(self, request):
        qs = Brand.objects.filter(is_active=True).order_by("name")
        return Response(BrandSerializer(qs, many=True).data)


class CategoryList(APIView):
    def get(self, request):
        qs = Category.objects.filter(is_active=True)
        section = (request.query_params.get("section") or "").strip().lower()
        if section in {Category.TYPE_PRODUCT, Category.TYPE_SERVICE, Category.TYPE_COURSE}:
            qs = qs.filter(type=section)
        qs = qs.order_by("name")
        return Response(CategorySerializer(qs, many=True).data)


class ProductList(APIView):
    def get(self, request):
        qs = Product.objects.filter(is_active=True)
        brand = request.query_params.get("brand")
        category = request.query_params.get("category")
        search = request.query_params.get("q")
        if brand:
            qs = qs.filter(brand__slug=brand)
        if category:
            qs = qs.filter(category__slug=category)
        if search:
            qs = qs.filter(title__icontains=search)
        qs = qs.select_related("brand", "category").prefetch_related("images", "variants").order_by("title")
        return Response(ProductListSerializer(qs, many=True).data)


class ProductDetail(APIView):
    def get(self, request, slug: str):
        product = get_object_or_404(
            Product.objects.select_related("brand", "category").prefetch_related("variants", "images"),
            slug=slug,
            is_active=True,
        )
        return Response(ProductDetailSerializer(product).data)


class CourseList(APIView):
    def get(self, request):
        qs = Course.objects.filter(is_active=True)
        category = request.query_params.get("category")
        search = request.query_params.get("q")
        if category:
            qs = qs.filter(category__slug=category)
        if search:
            qs = qs.filter(title__icontains=search)
        qs = qs.order_by("title")
        return Response(CourseListSerializer(qs, many=True).data)


class CourseDetail(APIView):
    def get(self, request, slug: str):
        course = get_object_or_404(Course, slug=slug, is_active=True)
        return Response(CourseDetailSerializer(course).data)


class ServiceList(APIView):
    def get(self, request):
        qs = Service.objects.filter(is_active=True)
        category = request.query_params.get("category")
        search = request.query_params.get("q")
        if category:
            qs = qs.filter(category__slug=category)
        if search:
            qs = qs.filter(title__icontains=search)
        qs = qs.order_by("title")
        return Response(ServiceListSerializer(qs, many=True).data)


class ServiceDetail(APIView):
    def get(self, request, slug: str):
        service = get_object_or_404(Service, slug=slug, is_active=True)
        return Response(ServiceDetailSerializer(service).data)

# --- Shipping & Cart Views ---

class ShippingMethodList(APIView):
    def get(self, request):
        methods = ShippingMethod.objects.filter(is_active=True).order_by("name")
        data = [{"code": m.code, "name": m.name, "base_rate": str(m.base_rate)} for m in methods]
        return Response(data)


class CartCreate(APIView):
    def post(self, request):
        currency = getattr(settings, "DEFAULT_CURRENCY", "INR")
        cart = Cart.objects.create(currency=currency)
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartDetail(APIView):
    def get(self, request, token: str):
        cart = get_object_or_404(
            Cart.objects.prefetch_related(
                "items__variant",
                "items__variant__images",
                "items__variant__product__images",
            ),
            token=token,
        )
        return Response(CartSerializer(cart).data)


class CartAddItem(APIView):
    def post(self, request, token: str):
        cart = get_object_or_404(Cart, token=token)
        serializer = CartAddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant_sku = serializer.validated_data["variant_sku"]
        quantity = int(serializer.validated_data["quantity"])

        variant = get_object_or_404(ProductVariant.objects.select_related("product"), sku=variant_sku, is_active=True)
        unit_price = Decimal(variant.sale_price)
        total_price = unit_price * quantity

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={"quantity": quantity, "unit_price_snapshot": unit_price, "total_price_snapshot": total_price},
        )
        if not created:
            item.quantity = quantity
            item.unit_price_snapshot = unit_price
            item.total_price_snapshot = total_price
            item.save()

        cart.refresh_from_db()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemUpdateDelete(APIView):
    def patch(self, request, token: str, variant_sku: str):
        cart = get_object_or_404(Cart, token=token)
        item = get_object_or_404(CartItem.objects.select_related("variant"), cart=cart, variant__sku=variant_sku)
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = int(serializer.validated_data["quantity"])
        unit_price = Decimal(item.unit_price_snapshot)
        item.quantity = quantity
        item.total_price_snapshot = unit_price * quantity
        item.save()
        cart.refresh_from_db()
        return Response(CartSerializer(cart).data)

    def delete(self, request, token: str, variant_sku: str):
        cart = get_object_or_404(Cart, token=token)
        item = get_object_or_404(CartItem, cart=cart, variant__sku=variant_sku)
        item.delete()
        cart.refresh_from_db()
        return Response(CartSerializer(cart).data)

# --- Checkout Views ---

class CheckoutView(APIView):
    def post(self, request):
        data = CheckoutRequestSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        token = data.validated_data["token"]
        cart = get_object_or_404(Cart.objects.prefetch_related("items__variant", "items__variant__product"), token=token)
        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        customer_name = data.validated_data["customer_name"]
        customer_email = data.validated_data.get("customer_email", "")
        customer_phone = data.validated_data.get("customer_phone", "")
        shipping_address = data.validated_data["shipping_address"]
        billing_address = data.validated_data.get("billing_address") or shipping_address
        shipping_method_code = data.validated_data["shipping_method_code"]
        coupon_code = data.validated_data.get("coupon_code", "").strip()

        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")
        for item in cart.items.all():
            unit_price = Decimal(item.unit_price_snapshot or 0)
            qty = Decimal(item.quantity or 0)
            subtotal += Decimal(item.total_price_snapshot or 0)
            
            # FIX 1: tax_rate None aanel 0 aakum
            tax_rate = Decimal(item.variant.tax_rate or 0)
            tax_total += (unit_price * qty * tax_rate / Decimal("100"))

        method = get_object_or_404(ShippingMethod, code=shipping_method_code, is_active=True)
        shipping_total = Decimal(method.base_rate or 0)

        discount_total = Decimal("0.00")
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code)
                if coupon.is_valid_now() and subtotal >= coupon.min_order_value:
                    if coupon.discount_type == Coupon.TYPE_AMOUNT:
                        discount_total = Decimal(coupon.value)
                    else:
                        discount_total = (subtotal * Decimal(coupon.value) / Decimal("100"))
                        if discount_total > subtotal:
                            discount_total = subtotal
                else:
                    coupon = None
            except Coupon.DoesNotExist:
                coupon = None

        grand_total = subtotal - discount_total + tax_total + shipping_total
        if grand_total < 0:
            grand_total = Decimal("0.00")

        order = Order.objects.create(
            order_number="",
            status=Order.STATUS_PENDING,
            payment_status=Order.PAYMENT_PENDING,
            subtotal=subtotal,
            discount_total=discount_total,
            tax_total=tax_total,
            shipping_total=shipping_total,
            grand_total=grand_total,
            currency=getattr(settings, "DEFAULT_CURRENCY", "INR"),
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            shipping_address=shipping_address,
            billing_address=billing_address,
            cart=cart,
            referral_code=coupon_code,
        )
        order.order_number = f"ORD{order.id:06d}"
        order.save(update_fields=["order_number"])

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.variant.product,
                variant=item.variant,
                title_snapshot=item.variant.product.title,
                sku_snapshot=item.variant.sku,
                quantity=item.quantity,
                unit_price_snapshot=item.unit_price_snapshot,
                total_price_snapshot=item.total_price_snapshot,
                tax_rate_snapshot=item.variant.tax_rate or 0, # FIX: None -> 0
            )

        intent = PaymentIntent.objects.create(
            order=order,
            provider=PaymentIntent.PROVIDER_RAZORPAY,
            client_secret="",
            amount=grand_total,
            currency=order.currency,
            status=PaymentIntent.STATUS_REQUIRES_ACTION,
            payload={},
        )

        rp_key_id = getattr(settings, "RAZORPAY_KEY_ID", "")
        rp_key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
        razorpay_order_id = ""
        
        # FIX 2: Razorpay call try-except il aakki
        if rp_key_id and rp_key_secret and intent.amount > 0:
            try:
                client = razorpay.Client(auth=(rp_key_id, rp_key_secret))
                amount_paise = int(Decimal(grand_total) * 100)
                rp_order = client.order.create(
                    {
                        "amount": amount_paise,
                        "currency": order.currency,
                        "receipt": order.order_number,
                        "payment_capture": 1,
                        "notes": {"order_number": order.order_number, "customer_name": customer_name, "customer_phone": customer_phone},
                    }
                )
                razorpay_order_id = rp_order.get("id", "")
                intent.payload = {"razorpay_order": rp_order}
                intent.save(update_fields=["payload"])
            except Exception as e:
                return Response({"detail": f"Razorpay Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        cart.status = Cart.STATUS_CONVERTED
        cart.save(update_fields=["status"])

        if coupon:
            Coupon.objects.filter(pk=coupon.pk).update(usage_count=F("usage_count") + 1)

        return Response(
            {
                "order_number": order.order_number,
                "totals": {
                    "subtotal": str(subtotal),
                    "discount_total": str(discount_total),
                    "tax_total": str(tax_total),
                    "shipping_total": str(shipping_total),
                    "grand_total": str(grand_total),
                },
                "payment_intent": {
                    "provider": intent.provider,
                    "amount": str(intent.amount),
                    "currency": intent.currency,
                    "status": intent.status,
                    "razorpay": {
                        "order_id": razorpay_order_id,
                        "key_id": rp_key_id,
                        "amount": int(Decimal(grand_total) * 100),
                        "currency": order.currency,
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )

class CourseCheckoutView(APIView):
    def post(self, request):
        data = CourseCheckoutRequestSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        slug = data.validated_data["course_slug"]
        course = get_object_or_404(Course, slug=slug, is_active=True)

        customer_name = data.validated_data["customer_name"]
        customer_email = data.validated_data.get("customer_email", "")
        customer_phone = data.validated_data.get("customer_phone", "")
        coupon_code = data.validated_data.get("coupon_code", "").strip()

        subtotal = Decimal(course.sale_price)
        tax_total = Decimal("0.00")
        shipping_total = Decimal("0.00")

        discount_total = Decimal("0.00")
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code)
                if coupon.is_valid_now() and subtotal >= coupon.min_order_value:
                    if coupon.discount_type == Coupon.TYPE_AMOUNT:
                        discount_total = Decimal(coupon.value)
                    else:
                        discount_total = (subtotal * Decimal(coupon.value) / Decimal("100"))
                        if discount_total > subtotal:
                            discount_total = subtotal
                else:
                    coupon = None
            except Coupon.DoesNotExist:
                coupon = None

        grand_total = subtotal - discount_total + tax_total + shipping_total
        if grand_total < 0:
            grand_total = Decimal("0.00")

        order = Order.objects.create(
            order_number="",
            status=Order.STATUS_PENDING,
            payment_status=Order.PAYMENT_PENDING,
            subtotal=subtotal,
            discount_total=discount_total,
            tax_total=tax_total,
            shipping_total=shipping_total,
            grand_total=grand_total,
            currency=getattr(settings, "DEFAULT_CURRENCY", "INR"),
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            shipping_address={},
            billing_address={},
            referral_code=coupon_code,
        )
        order.order_number = f"ORD{order.id:06d}"
        order.save(update_fields=["order_number"])

        OrderItem.objects.create(
            order=order,
            product=None,
            variant=None,
            title_snapshot=course.title,
            sku_snapshot=f"COURSE-{course.slug}",
            quantity=1,
            unit_price_snapshot=subtotal,
            total_price_snapshot=grand_total,
            tax_rate_snapshot=Decimal("0.00"),
        )

        intent = PaymentIntent.objects.create(
            order=order,
            provider=PaymentIntent.PROVIDER_RAZORPAY,
            client_secret="",
            amount=grand_total,
            currency=order.currency,
            status=PaymentIntent.STATUS_REQUIRES_ACTION,
            payload={},
        )

        rp_key_id = getattr(settings, "RAZORPAY_KEY_ID", "")
        rp_key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
        razorpay_order_id = ""
        if rp_key_id and rp_key_secret and intent.amount > 0:
            client = razorpay.Client(auth=(rp_key_id, rp_key_secret))
            amount_paise = int(grand_total * 100)
            rp_order = client.order.create(
                {
                    "amount": amount_paise,
                    "currency": order.currency,
                    "receipt": order.order_number,
                    "payment_capture": 1,
                    "notes": {"order_number": order.order_number, "customer_name": customer_name, "customer_phone": customer_phone},
                }
            )
            razorpay_order_id = rp_order.get("id", "")
            intent.payload = {"razorpay_order": rp_order}
            intent.save(update_fields=["payload"])

        if coupon:
            Coupon.objects.filter(pk=coupon.pk).update(usage_count=F("usage_count") + 1)

        return Response(
            {
                "order_number": order.order_number,
                "totals": {
                    "subtotal": str(subtotal),
                    "discount_total": str(discount_total),
                    "tax_total": str(tax_total),
                    "shipping_total": str(shipping_total),
                    "grand_total": str(grand_total),
                },
                "payment_intent": {
                    "provider": intent.provider,
                    "amount": str(intent.amount),
                    "currency": intent.currency,
                    "status": intent.status,
                    "razorpay": {
                        "order_id": razorpay_order_id,
                        "key_id": rp_key_id,
                        "amount": int(grand_total * 100),
                        "currency": order.currency,
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )


class ServiceCheckoutView(APIView):
    def post(self, request):
        data = ServiceCheckoutRequestSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        slug = data.validated_data["service_slug"]
        service = get_object_or_404(Service, slug=slug, is_active=True)

        customer_name = data.validated_data["customer_name"]
        customer_email = data.validated_data.get("customer_email", "")
        customer_phone = data.validated_data.get("customer_phone", "")
        coupon_code = data.validated_data.get("coupon_code", "").strip()

        subtotal = Decimal(service.base_price)
        tax_total = Decimal("0.00")
        shipping_total = Decimal("0.00")

        discount_total = Decimal("0.00")
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code)
                if coupon.is_valid_now() and subtotal >= coupon.min_order_value:
                    if coupon.discount_type == Coupon.TYPE_AMOUNT:
                        discount_total = Decimal(coupon.value)
                    else:
                        discount_total = (subtotal * Decimal(coupon.value) / Decimal("100"))
                        if discount_total > subtotal:
                            discount_total = subtotal
                else:
                    coupon = None
            except Coupon.DoesNotExist:
                coupon = None

        grand_total = subtotal - discount_total + tax_total + shipping_total
        if grand_total < 0:
            grand_total = Decimal("0.00")

        order = Order.objects.create(
            order_number="",
            status=Order.STATUS_PENDING,
            payment_status=Order.PAYMENT_PENDING,
            subtotal=subtotal,
            discount_total=discount_total,
            tax_total=tax_total,
            shipping_total=shipping_total,
            grand_total=grand_total,
            currency=getattr(settings, "DEFAULT_CURRENCY", "INR"),
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            shipping_address={},
            billing_address={},
            referral_code=coupon_code,
        )
        order.order_number = f"ORD{order.id:06d}"
        order.save(update_fields=["order_number"])

        OrderItem.objects.create(
            order=order,
            product=None,
            variant=None,
            title_snapshot=service.title,
            sku_snapshot=f"SERVICE-{service.slug}",
            quantity=1,
            unit_price_snapshot=subtotal,
            total_price_snapshot=grand_total,
            tax_rate_snapshot=Decimal("0.00"),
        )

        intent = PaymentIntent.objects.create(
            order=order,
            provider=PaymentIntent.PROVIDER_RAZORPAY,
            client_secret="",
            amount=grand_total,
            currency=order.currency,
            status=PaymentIntent.STATUS_REQUIRES_ACTION,
            payload={},
        )

        rp_key_id = getattr(settings, "RAZORPAY_KEY_ID", "")
        rp_key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
        razorpay_order_id = ""
        if rp_key_id and rp_key_secret and intent.amount > 0:
            client = razorpay.Client(auth=(rp_key_id, rp_key_secret))
            amount_paise = int(grand_total * 100)
            rp_order = client.order.create(
                {
                    "amount": amount_paise,
                    "currency": order.currency,
                    "receipt": order.order_number,
                    "payment_capture": 1,
                    "notes": {"order_number": order.order_number, "customer_name": customer_name, "customer_phone": customer_phone},
                }
            )
            razorpay_order_id = rp_order.get("id", "")
            intent.payload = {"razorpay_order": rp_order}
            intent.save(update_fields=["payload"])

        if coupon:
            Coupon.objects.filter(pk=coupon.pk).update(usage_count=F("usage_count") + 1)

        return Response(
            {
                "order_number": order.order_number,
                "totals": {
                    "subtotal": str(subtotal),
                    "discount_total": str(discount_total),
                    "tax_total": str(tax_total),
                    "shipping_total": str(shipping_total),
                    "grand_total": str(grand_total),
                },
                "payment_intent": {
                    "provider": intent.provider,
                    "amount": str(intent.amount),
                    "currency": intent.currency,
                    "status": intent.status,
                    "razorpay": {
                        "order_id": razorpay_order_id,
                        "key_id": rp_key_id,
                        "amount": int(grand_total * 100),
                        "currency": order.currency,
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )

# --- Verification & Orders Views ---

class RazorpayVerifyView(APIView):
    def post(self, request):
        serializer = RazorpayVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_number = serializer.validated_data["order_number"]
        razorpay_order_id = serializer.validated_data["razorpay_order_id"]
        razorpay_payment_id = serializer.validated_data["razorpay_payment_id"]
        razorpay_signature = serializer.validated_data["razorpay_signature"]

        order = get_object_or_404(Order, order_number=order_number)
        intent = order.payment_intents.filter(provider=PaymentIntent.PROVIDER_RAZORPAY).last()
        if not intent:
            return Response({"detail": "Payment intent not found"}, status=status.HTTP_400_BAD_REQUEST)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                }
            )
        except Exception:
            intent.status = PaymentIntent.STATUS_CANCELED
            intent.save(update_fields=["status"])
            order.payment_status = Order.PAYMENT_FAILED
            order.save(update_fields=["payment_status"])
            return Response({"detail": "Signature verification failed"}, status=status.HTTP_400_BAD_REQUEST)

        PaymentTransaction.objects.create(
            intent=intent,
            provider_txn_id=razorpay_payment_id,
            event=PaymentTransaction.EVENT_CAPTURED,
            amount=intent.amount,
            status="captured",
            payload={
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            },
        )

        intent.status = PaymentIntent.STATUS_SUCCEEDED
        intent.save(update_fields=["status"])
        order.payment_status = Order.PAYMENT_PAID
        order.paid_at = timezone.now()
        order.status = Order.STATUS_CONFIRMED
        order.save(update_fields=["payment_status", "paid_at", "status"])

        try:
            if getattr(order, "cart_id", None):
                cart = order.cart
                cart.items.all().delete()
        except Exception:
            pass

        try:
            if getattr(order, "referral_code", "") and not getattr(order, "referral_credited", False):
                commission_total = Decimal("0.00")
                purchaser_name = order.customer_name
                for it in order.items.all():
                    try:
                        if getattr(it, "product_id", None) and getattr(it.product, "referral_commission", None) is not None:
                            commission_total += Decimal(it.product.referral_commission)
                            continue
                    except Exception:
                        pass
                    sku = (it.sku_snapshot or "").upper()
                    try:
                        if sku.startswith("COURSE-"):
                            slug = it.sku_snapshot.split("COURSE-", 1)[1]
                            c = Course.objects.filter(slug=slug).first()
                            if c and c.referral_commission is not None:
                                commission_total += Decimal(c.referral_commission)
                        elif sku.startswith("SERVICE-"):
                            slug = it.sku_snapshot.split("SERVICE-", 1)[1]
                            s = Service.objects.filter(slug=slug).first()
                            if s and s.referral_commission is not None:
                                commission_total += Decimal(s.referral_commission)
                    except Exception:
                        pass

                if commission_total > 0:
                    import json as _json
                    from urllib import request as _urlreq
                    from urllib.error import URLError as _URLError, HTTPError as _HTTPError
                    jora_base = getattr(settings, "JORA_BASE_URL", "http://localhost:4001/api/v1")
                    if not (jora_base.startswith("http://") or jora_base.startswith("https://")):
                        jora_base = f"https://{jora_base}"
                    url = jora_base.rstrip("/") + "/wallet/creditReferralByCode"
                    payload = _json.dumps({
                        "referralCode": order.referral_code,
                        "purchaserName": purchaser_name,
                        "amount": float(commission_total),
                    }).encode("utf-8")
                    req = _urlreq.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
                    try:
                        resp = _urlreq.urlopen(req, timeout=10)
                        logging.info("Referral credit request succeeded: %s %s", resp.getcode(), url)
                        order.referral_credited = True
                        order.save(update_fields=["referral_credited"])
                    except _HTTPError as e:
                        logging.warning("Referral credit HTTP error: %s %s", e.code, url)
                    except _URLError as e:
                        logging.warning("Referral credit request failed: %s %s", getattr(e, 'reason', e), url)
        except Exception:
            pass

        return Response({"detail": "Payment verified", "order_number": order_number})


class OrdersList(APIView):
    def get(self, request):
        phone = request.query_params.get("phone", "").strip()
        email = request.query_params.get("email", "").strip()
        if not phone and not email:
            return Response({"detail": "Provide phone or email"}, status=status.HTTP_400_BAD_REQUEST)

        qs = Order.objects.all().order_by("-created_at")
        if phone:
            qs = qs.filter(customer_phone__iexact=phone)
        if email:
            qs = qs.filter(customer_email__iexact=email)

        data = [
            {
                "order_number": o.order_number,
                "status": o.status,
                "payment_status": o.payment_status,
                "grand_total": str(o.grand_total),
                "currency": o.currency,
                "placed_at": getattr(o, "placed_at", None),
                "paid_at": getattr(o, "paid_at", None),
                "items": [
                    {
                        "sku": it.sku_snapshot,
                        "title": it.title_snapshot,
                        "quantity": it.quantity,
                        "unit_price": str(it.unit_price_snapshot),
                        "total_price": str(it.total_price_snapshot),
                    }
                    for it in o.items.all()
                ],
            }
            for o in qs
        ]
        return Response(data)


class ProductReviews(APIView):
    def get(self, request, slug: str):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        qs = product.reviews.filter(is_approved=True).order_by("-created_at")
        return Response(ReviewSerializer(qs, many=True).data)

    def post(self, request, slug: str):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        r = Review.objects.create(
            product=product,
            rating=serializer.validated_data["rating"],
            title=serializer.validated_data.get("title", ""),
            body=serializer.validated_data.get("body", ""),
            name_or_email=serializer.validated_data.get("name_or_email", ""),
            is_approved=False,
        )
        return Response(ReviewSerializer(r).data, status=status.HTTP_201_CREATED)
    
class GuestOrderSearchView(APIView):
    permission_classes = [] 

    def get(self, request):
        phone = request.query_params.get("phone", "").strip()
        email = request.query_params.get("email", "").strip()

        if not phone and not email:
            return Response({"error": "Phone or Email required"}, status=400)

        orders = Order.objects.filter(
            Q(customer_phone=phone) | Q(customer_email=email)
        ).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product', 'course', 'service', 'variant'))
        ).order_by("-placed_at")

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    

class CouponVerifyView(APIView):
    def post(self, request):
        code = (
            request.data.get("code") 
            or request.data.get("coupon_code") 
            or request.data.get("referral_code") 
            or ""
        ).strip()
        
        if not code:
            return Response({"detail": "Code required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
          
            coupon = Coupon.objects.get(code__iexact=code)
            
            # is_valid_now() check
            if not coupon.is_valid_now():
                return Response({"detail": "Coupon expired / inactive / limit reached"}, status=status.HTTP_400_BAD_REQUEST)
            
         
            return Response({
                "code": coupon.code,
                "discount_value": str(coupon.value),
                "value": str(coupon.value),
                "discount_type": coupon.discount_type,
                "min_order_value": str(coupon.min_order_value),
                "is_valid": True
            })
        
        except Coupon.DoesNotExist:
            return Response({"detail": "Invalid Referral Code"}, status=status.HTTP_400_BAD_REQUEST)