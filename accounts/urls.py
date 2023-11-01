from django.urls import path
from .views import UserDetailsView

app_name = "accounts"

urlpatterns =[
    path("", UserDetailsView.as_view()),
]
