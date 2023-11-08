from django.urls import path
<<<<<<< HEAD
from .views import UserDetailsView
=======
from accounts import views
>>>>>>> df5e2641355519a0f2b41de1888e6225cd00d71b

app_name = "accounts"

urlpatterns =[
<<<<<<< HEAD
    path("", UserDetailsView.as_view()),
=======
    path("", views.UserDetailsView.as_view()),
    path("locations/", views.LocationListView.as_view()),
    path("test/", views.testAPI.as_view()),
>>>>>>> df5e2641355519a0f2b41de1888e6225cd00d71b
]
