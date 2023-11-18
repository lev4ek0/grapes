from rest_framework.generics import ListAPIView

from geography.models import Region
from geography.serializers import RegionSerializer


class RegionListAPIView(ListAPIView):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
