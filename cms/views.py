from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from dal import autocomplete

from .models import Banner, Page
from .serializers import BannerSerializer, PageSerializer
from catalog.models import Brand, Category, Product


class BannerList(APIView):
    def get(self, request):
        placement = request.query_params.get("placement")
        qs = Banner.objects.filter(is_active=True)
        if placement:
            qs = qs.filter(placement=placement)
        qs = qs.order_by("sort_order", "-created_at")
        data = BannerSerializer(qs, many=True, context={"request": request}).data
        return Response(data)


class PageDetail(APIView):
    def get(self, request, slug: str):
        page = get_object_or_404(Page, slug=slug, is_published=True)
        data = PageSerializer(page).data
        return Response(data, status=status.HTTP_200_OK)


class BannerLinkAutocomplete(autocomplete.Select2ListView):
    """
    Returns a unified list of link targets for banners.
    id: link_path to be saved (e.g., "/products?brand=nike")
    text: human-readable label to display in admin
    """

    def get_list(self):
        q = (self.q or "").strip().lower()

        results = []
        # Static routes
        static_options = [
            ("/products", "Products - All"),
            ("/categories", "Categories"),
            ("/brands", "Brands"),
            ("/cart", "Cart"),
            ("/checkout", "Checkout"),
        ]
        for path, label in static_options:
            if not q or q in label.lower() or q in path.lower():
                results.append((path, label))

        # Brands
        brands_qs = Brand.objects.filter(is_active=True)
        if q:
            brands_qs = brands_qs.filter(name__icontains=q)
        for b in brands_qs.order_by("name")[:20]:
            results.append((f"/products?brand={b.slug}", f"Brand: {b.name}"))

        # Categories
        cats_qs = Category.objects.filter(is_active=True)
        if q:
            cats_qs = cats_qs.filter(name__icontains=q)
        for c in cats_qs.order_by("name")[:20]:
            results.append((f"/products?category={c.slug}", f"Category: {c.name}"))

        # Products
        prods_qs = Product.objects.filter(is_active=True)
        if q:
            prods_qs = prods_qs.filter(title__icontains=q)
        for p in prods_qs.order_by("title")[:20]:
            results.append((f"/product/{p.slug}", f"Product: {p.title}"))

        return results
