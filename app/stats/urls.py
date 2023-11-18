from django.urls import path

from stats import views

urlpatterns = [
    path("forecast/worst/<slug:date>", views.WorstForecastAPIView.as_view()),
    path("forecast/map/<slug:date>", views.ForecastMapAPIView.as_view()),
]
