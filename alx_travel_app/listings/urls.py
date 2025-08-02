from rest_framework import routers
from django.urls import include, path

from .views import ListingViewset, BookingViewSet

app_router = routers.DefaultRouter()
app_router.register(r"listings", ListingViewset, basename="listings")
app_router.register(r"bookings", BookingViewSet, basename="bookings")

urlpatterns = [
    # path("", include((main_router.urls, "chats"), namespace="chats")),
    path("", include(app_router.urls)),
]
