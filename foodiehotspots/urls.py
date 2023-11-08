from django.urls import path
from foodiehotspots import views

app_name = "foodiehotspots"

<<<<<<< HEAD
urlpatterns =[
    # path("", views.List.as_view()),
]
=======
urlpatterns = [
    path("", views.RestaurantList.as_view()),
    path("<int:pk>", views.FoodieDetailsView.as_view()),
    path("<int:pk>/evaluation", views.EvalCreateView.as_view()),
]
>>>>>>> df5e2641355519a0f2b41de1888e6225cd00d71b
