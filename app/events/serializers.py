from rest_framework import serializers

from events.models import Event


class EventSerializer(serializers.ModelSerializer):
    region_id = serializers.IntegerField()
    region_name = serializers.CharField(source="region.name", read_only=True)
    
    def create(self, validated_data):
        event = Event.objects.create(**validated_data)
        return event

    class Meta:
        model = Event
        fields = ("id", "date", "temp", "humidity", "notes", "region_id", "region_name")
