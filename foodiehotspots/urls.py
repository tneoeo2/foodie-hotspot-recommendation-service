from django.urls import path
from foodiehotspots import views

app_name = "foodiehotspots"

urlpatterns = [
    path("", views.RestaurantList.as_view()),
    path("<int:pk>", views.FoodieDetailsView.as_view()),
    path("<int:pk>/evaluation", views.EvalCreateView.as_view()),
]
