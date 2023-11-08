from django.urls import path
from accounts import views

app_name = "accounts"

urlpatterns =[
    path("", views.UserDetailsView.as_view()),
    path("locations/", views.LocationListView.as_view()),
    path("test/", views.testAPI.as_view()),
]
