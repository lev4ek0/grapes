from rest_framework import serializers
from geography.models import Region

from stats.utils import get_color_code_by_number


class DateSerializer(serializers.Serializer):
    date = serializers.DateField(required=True, input_formats=["%d-%m-%Y"])


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ("id", "name", "code")
