from rest_framework import serializers

from geography.models import Region
from stats.models import Illness


class DateSerializer(serializers.Serializer):
    date = serializers.DateField(required=True, input_formats=["%d-%m-%Y"])


class IllnessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Illness
        fields = ("id", "name")


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ("id", "name", "code")
