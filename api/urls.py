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
    path("courses/checkout/", views.CourseCheckoutView.as_view(), name="courses-checkout"),
    path("courses/<slug:slug>/", views.CourseDetail.as_view(), name="course-detail"),

    # Services
    path("services/", views.ServiceList.as_view(), name="services-list"),
    path("services/checkout/", views.ServiceCheckoutView.as_view(), name="services-checkout"),
    path("services/<slug:slug>/", views.ServiceDetail.as_view(), name="service-detail"),

    # Shipping
    path("shipping/methods/", views.ShippingMethodList.as_view(), name="shipping-methods"),

    # Cart
    path("cart/", views.CartCreate.as_view(), name="cart-create"),
    path("cart/<str:token>/", views.CartDetail.as_view(), name="cart-detail"),
    path("cart/<str:token>/add/", views.CartAddItem.as_view(), name="cart-add-item"),
    path("cart/<str:token>/items/<str:variant_sku>/", views.CartItemUpdateDelete.as_view(), name="cart-item-update-delete"),
    path("cart/<str:token>/item/<str:variant_sku>/", views.CartItemUpdateDelete.as_view(), name="cart-item-update-delete-alt"),

    # Checkout & Payments
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    #path("checkout/direct/", views.DirectCheckoutView.as_view(), name="checkout-direct"), 
    path("payment/razorpay/verify/", views.RazorpayVerifyView.as_view(), name="razorpay-verify"),
    
    # Orders
    path("orders/", views.OrdersList.as_view(), name="orders-list"),
    path("orders/guest-search/", views.GuestOrderSearchView.as_view(), name="orders-guest-search"), 
    path("coupons/verify/", views.CouponVerifyView.as_view(), name="coupons-verify"),
    path("referrals/verify/",views.CouponVerifyView.as_view(), name="referrals-verify-alias"),
]