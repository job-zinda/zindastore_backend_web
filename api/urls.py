from django.urls import path
from . import views

urlpatterns = [
    # Catalog
    path("brands/", views.BrandList.as_view(), name="brands-list"),
    path("categories/", views.CategoryList.as_view(), name="categories-list"),
    path("products/", views.ProductList.as_view(), name="products-list"),
    path("products/<slug:slug>/", views.ProductDetail.as_view(), name="products-detail"),
    path("products/<slug:slug>/reviews/", views.ProductReviews.as_view(), name="products-reviews"),
    # Courses
    path("courses/", views.CourseList.as_view(), name="courses-list"),
    # Place checkout BEFORE the slug route to avoid 'checkout' being captured as a slug
    path("courses/checkout/", views.CourseCheckoutView.as_view(), name="courses-checkout"),
    path("courses/<slug:slug>/", views.CourseDetail.as_view(), name="course-detail"),
    # Services
    path("services/", views.ServicesList.as_view(), name="services-list"),
    path("service/<slug:slug>/", views.ServiceDetail.as_view(), name="service-detail"),
    path("services/checkout/", views.ServiceCheckoutView.as_view(), name="services-checkout"),

    # Shipping
    path("shipping/methods/", views.ShippingMethodList.as_view(), name="shipping-methods"),

    # Cart (guest)
    path("cart/", views.CartCreate.as_view(), name="cart-create"),
    path("cart/<str:token>/", views.CartDetail.as_view(), name="cart-detail"),
    path("cart/<str:token>/items/", views.CartAddItem.as_view(), name="cart-add-item"),
    path("cart/<str:token>/items/<str:variant_sku>/", views.CartItemUpdateDelete.as_view(), name="cart-item-update-delete"),
    # Checkout
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    # Payment verification
    path("payment/razorpay/verify/", views.RazorpayVerifyView.as_view(), name="razorpay-verify"),
    # Orders (guest lookup)
    path("orders/", views.OrdersList.as_view(), name="orders-list"),
]
