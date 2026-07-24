from django.urls import path
from . import views

urlpatterns = [
    path("banners/", views.BannerList.as_view(), name="cms-banners-list"),
    path("pages/<slug:slug>/", views.PageDetail.as_view(), name="cms-page-detail"),
    # Admin autocomplete for banner link_path
    path("autocomplete/banner-link/", views.BannerLinkAutocomplete.as_view(), name="cms-banner-link-autocomplete"),
]
