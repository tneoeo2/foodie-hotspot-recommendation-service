from django.urls import path
from accounts.views import UserDetailsView, LocationListView

app_name = "accounts"

urlpatterns =[
    path("", UserDetailsView.as_view()),
    path("locations/", LocationListView.as_view()),
]
