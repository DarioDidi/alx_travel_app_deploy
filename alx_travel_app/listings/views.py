from rest_framework import viewsets

from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from .permissions import IsBookingOwner

# Create your views here.


class ListingViewset(viewsets.ModelViewSet):
    serializer_class = ListingSerializer

    def get_queryset(self):
        return Listing.objects.all()


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsBookingOwner]

    def get_queryset(self):
        return Booking.objects.filter(quest=self.request.user)
