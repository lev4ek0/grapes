from django.urls import path
from geography import views

urlpatterns = [
    path("regions", views.RegionListAPIView.as_view()),
]
