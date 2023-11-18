from copy import deepcopy

from rest_framework.request import Request
from rest_framework.views import APIView, Response
from rest_framework.generics import ListAPIView
from stats.models import Illness

from geography.models import Region
from processing.forecast import forecast
from stats.serializers import DateSerializer, IllnessSerializer, RegionSerializer
from stats.utils import get_color_code_by_number


class IllnessListAPIView(ListAPIView):
    queryset = Illness.objects.all()
    serializer_class = IllnessSerializer


def get_query_params(func):
    def wrapper(self, request, **kwargs):
        regions_list = request.query_params.getlist("region_ids")
        if regions_list:
            regions = Region.objects.filter(id__in=regions_list)
        else:
            regions = Region.objects.all()
        kwargs["regions"] = regions
        kwargs["limit"] = int(request.query_params.get("limit", 5))
        illnesses_list = request.query_params.getlist("illness_ids")
        if illnesses_list:
            illnesses = Illness.objects.filter(id__in=illnesses_list)
        else:
            illnesses = Illness.objects.all()
        kwargs["illnesses"] = set(illnesses.values_list('name', flat=True))
        return func(self, request, **kwargs)
    return wrapper


class WorstForecastAPIView(APIView):
    @get_query_params
    def get(self, request: Request, date: str, regions: list[Region], limit: int, illnesses: set[str]):
        serialized_date = DateSerializer(data={"date": date})
        if not serialized_date.is_valid():
            return Response(status=404)
        forecasts = []
        for region in regions:
            forecast_result = deepcopy(forecast(serialized_date.data["date"], region.pk))
            forecast_result["region"] = RegionSerializer(region).data
            forecast_result["illnesses"] = list(filter(lambda x: x["name"] in illnesses, forecast_result["illnesses"]))
            forecasts.append(forecast_result)
        forecasts.sort(key=lambda x: sum(map(lambda y: y["percent"], x["illnesses"])), reverse=True)
        return Response(forecasts[:limit])


class ForecastMapAPIView(APIView):
    @get_query_params
    def get(self, request: Request, date: str, regions: list[Region], illnesses: set[str], **kwargs):
        serialized_date = DateSerializer(data={"date": date})
        if not serialized_date.is_valid():
            return Response(status=404)
        forecasts = []
        for region in regions:
            forecast_result = deepcopy(forecast(serialized_date.data["date"], region.pk))
            forecast_result["region"] = RegionSerializer(region).data
            forecast_result["illnesses"] = list(filter(lambda x: x["name"] in illnesses, forecast_result["illnesses"]))
            forecasts.append(forecast_result)
        min_value = min(map(lambda x: sum(map(lambda y: y["percent"], x["illnesses"])), forecasts))
        max_value = max(map(lambda x: sum(map(lambda y: y["percent"], x["illnesses"])), forecasts))
        for forecast_ in forecasts:
            forecast_["color"] = get_color_code_by_number(
                sum(map(lambda y: y["percent"], forecast_["illnesses"])), max_value, min_value
            )
            del forecast_["weather_forecast"]
            del forecast_["date"]
        return Response(forecasts)
