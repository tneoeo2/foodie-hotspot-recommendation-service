from django.urls import path
from foodiehotspots import views

app_name = "foodiehotspots"

urlpatterns =[
    path("", views.RestaurantList.as_view()),
]
