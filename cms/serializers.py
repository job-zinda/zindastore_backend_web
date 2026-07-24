from rest_framework import serializers
from .models import Banner, Page


class BannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = [
            "id",
            "title",
            "image_url",
            "link_url",
            "link_path",
            "placement",
            "sort_order",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["slug", "title", "body"]
