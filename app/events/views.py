from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView

from events.models import Event
from events.serializers import EventSerializer


class EventsListCreateView(ListCreateAPIView):
    filterset_fields = ("region_id",)
    queryset = Event.objects.select_related("region")
    serializer_class = EventSerializer
