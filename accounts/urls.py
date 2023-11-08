from django.urls import path
from accounts.views import UserDetailsView, LocationListView, testAPI

app_name = "accounts"

urlpatterns =[
    path("", UserDetailsView.as_view()),
    path("locations/", LocationListView.as_view()),
    path("test/", testAPI.as_view())
]
