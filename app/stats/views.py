from collections import defaultdict
from copy import deepcopy
import datetime
import math

from rest_framework.request import Request
from rest_framework.views import APIView, Response
from rest_framework.generics import ListAPIView
from stats.models import Illness

from geography.models import Region
from processing.forecast import get_forecast
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
        kwargs["mode"] = request.query_params.get("mode", "percent")
        illnesses_list = request.query_params.getlist("illness_ids")
        if illnesses_list:
            illnesses = Illness.objects.filter(id__in=illnesses_list)
        else:
            illnesses = Illness.objects.all()
        kwargs["illnesses"] = set(illnesses.values_list('name', flat=True))
        return func(self, request, **kwargs)
    return wrapper


class HeatMapAPIView(APIView):
    @get_query_params
    def get(self, request: Request, date: str, regions: list[Region], illnesses: set[str], mode: str, **kwargs):
        serialized_date = DateSerializer(data={"date": date})
        if not serialized_date.is_valid():
            return Response(status=404)
        forecasts = []
        date = serialized_date.data["date"]
        output = {
            "dates": [],
            "data": [],
            "illnesses": [],
            "forecast": [],
        }
        for day_index in range(-6, 4):
            cur_date = datetime.datetime.strptime(serialized_date.data["date"], "%Y-%m-%d") + datetime.timedelta(days=day_index)
            illness_map = {illness: 0 for illness in illnesses}
            for region in regions:
                forecast_result = deepcopy(get_forecast(cur_date.strftime("%Y-%m-%d"), region.pk))
                for illness in list(filter(lambda x: x["name"] in illnesses, forecast_result["illnesses"])):
                    if mode == 'percent':
                        illness_map[illness["name"]] += illness["percent"]
                    else:
                        illness_map[illness["name"]] += 1
            forecasts.append(illness_map)
            output["dates"].append(cur_date.strftime("%d-%m-%Y"))
        
        output["illnesses"] = sorted(illness_map.keys(), key=lambda x: x[0])
        minimum = math.inf
        maximum = 0
        for x in range(len(forecasts)):
            key = "data" if x < 7 else "forecast"
            for y, (illness, value) in enumerate(sorted(forecasts[x].items(), key=lambda x: x[0])):
                if mode == 'percent':
                    val = round(value/len(regions), 2)
                    output[key].append([x, y, val if value else '-'])
                else:
                    val = value
                    output[key].append([x, y, val if value else '-'])
                maximum, minimum = max(maximum, val), min(minimum, val)
        output["max"], output["min"] = maximum, minimum
        return Response(output)


class WorstForecastAPIView(APIView):
    @get_query_params
    def get(self, request: Request, date: str, regions: list[Region], limit: int, illnesses: set[str], **kwargs):
        serialized_date = DateSerializer(data={"date": date})
        if not serialized_date.is_valid():
            return Response(status=404)
        forecasts = []
        date = serialized_date.data["date"]
        for region in regions:
            forecast_result = deepcopy(get_forecast(date, region.pk))
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
        date = serialized_date.data["date"]
        for region in regions:
            forecast_result = deepcopy(get_forecast(date, region.pk))
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
