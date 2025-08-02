from rest_framework import permissions
from .models import Booking

from django.shortcuts import get_object_or_404


class IsBookingOwner(permissions.BasePermission):
    message = "Access Denied!"

    def has_permission(self, request, view):
        user = request.user
        booking = self.get_object()
        return user.is_authenticated() and booking.quest == request.user

    def has_object_permission(self, request, view, obj):

        if request.method in ["GET", "PUT", "PATCH", "DELETE"]:
            # Instance must have an attribute named `owner`.
            return obj.guest == request.user

    def get_object(self):
        obj = get_object_or_404(Booking, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj
