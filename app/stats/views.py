from copy import deepcopy

from rest_framework.request import Request
from rest_framework.views import APIView, Response

from geography.models import Region
from processing.forecast import forecast
from stats.serializers import DateSerializer, RegionSerializer
from stats.utils import get_color_code_by_number


class WorstForecastAPIView(APIView):
    def get(self, request: Request, date: str):
        serialized_date = DateSerializer(data={"date": date})
        regions = Region.objects.all()
        if not serialized_date.is_valid():
            return Response(status=404)
        forecasts = []
        for region in regions:
            forecast_result = forecast(serialized_date.data["date"], region.pk)
            forecast_result["region"] = RegionSerializer(region).data
            forecasts.append(forecast_result)
        forecasts.sort(key=lambda x: sum(x["illnesses"].values()), reverse=True)
        return Response(forecasts[: int(request.query_params.get("limit", 5))])


class ForecastMapAPIView(APIView):
    def get(self, request: Request, date: str):
        serialized_date = DateSerializer(data={"date": date})
        regions = Region.objects.all()
        if not serialized_date.is_valid():
            return Response(status=404)
        forecasts = []
        for region in regions:
            forecast_result = forecast(serialized_date.data["date"], region.pk)
            forecast_result["region"] = RegionSerializer(region).data
            forecasts.append(forecast_result)
        min_value = min(map(lambda x: sum(x["illnesses"].values()), forecasts))
        max_value = max(map(lambda x: sum(x["illnesses"].values()), forecasts))
        for forecast_ in deepcopy(forecasts):
            forecast_["color"] = get_color_code_by_number(
                sum(forecast_["illnesses"].values()), max_value, min_value
            )
            del forecast_["weather_forecast"]
            del forecast_["date"]
        return Response(forecasts)
