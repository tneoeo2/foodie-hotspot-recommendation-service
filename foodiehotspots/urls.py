from django.urls import path
from foodiehotspots.views import FoodieDetailsView, EvalCreateView, RestaurantList
app_name = "foodiehotspots"

urlpatterns =[
    path("", RestaurantList.as_view()),
    path("<int:pk>", FoodieDetailsView.as_view()),
    path("<int:pk>/evaluation", EvalCreateView.as_view()),
]
