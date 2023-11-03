from django.urls import path
from .views import FoodieDetailsView, EvalCreateView

app_name = "foodiehotspots"

urlpatterns =[
    path("<int:pk>", FoodieDetailsView.as_view()),
    path("<int:pk>/evaluation", EvalCreateView.as_view()),
]
