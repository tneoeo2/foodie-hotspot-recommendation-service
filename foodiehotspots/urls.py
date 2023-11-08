from django.urls import path
from foodiehotspots.views import FoodieDetailsView, EvalCreateView

app_name = "foodiehotspots"

urlpatterns =[
    path("", views.RestaurantList.as_view()),
    path("<int:pk>", FoodieDetailsView.as_view()),
    path("<int:pk>/evaluation", EvalCreateView.as_view()),
]
