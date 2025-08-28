import os
import requests

from .permissions import IsBookingOwner
from .serializers import ListingSerializer, BookingSerializer
from .models import Listing, Booking, PaymentStatus, Payment
from .tasks import send_confirmation_email

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from dotenv import load_dotenv
load_dotenv()
CHAPA_SECRET_KEY = os.getenv('CHAPA_SECRET_KEY')


# Create your views here.


class ListingViewset(viewsets.ModelViewSet):
    serializer_class = ListingSerializer

    def get_queryset(self):
        return Listing.objects.all()


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsBookingOwner]

    def create(self, validated_data):
        booking = super().create(**validated_data)
        mail = self.request.user.email
        content = f"booking confirmed with id:{booking.id}"
        send_confirmation_email.delay(mail, content)
        return booking

    def get_queryset(self):
        return Booking.objects.filter(quest=self.request.user)


class PayView(APIView):
    def post(self):
        data = self.request.data
        booking_reference = data.get('booking_reference')
        amount = data.get('amount')
        email = data.get('email')
        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": email,
            "tx_ref": booking_reference,
            "return_url": "https://yourdomain.com/payment/verify/",
            "callback_url":
                "https://webhook.site/077164d6-29cb-40df-ba29-8a00e59a7e60",
        }
        url = "https://api.chapa.co/v1/transaction/initialize"

        headers = {
            'Authorization': f'Bearer {CHAPA_SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, json=payload, headers=headers)

        res = response.text

        print(res)
        if res.status == "success":
            payment = Payment.objects.create(
                booking_reference=booking_reference,
                amount=amount,
                transaction_id=res['data']['tx_ref'],
                status='Pending'
            )
            return Response({
                "checkout_url": res['data']['checkout_url'],
                "payment_id": payment.id
            })
        return Response({"error": res.get('message')},
                        status=400)


class VerifyView(APIView):
    def get(self, request, tx_ref):
        url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
        payload = ''
        headers = {
            'Authorization': f'Bearer {CHAPA_SECRET_KEY}'
        }
        response = requests.get(url, headers=headers, data=payload)
        data = response.text

        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Payment does not exist"}, status=404)

        if data.get('status') == 'success'\
                and data['data']['status'] == 'success':
            payment.status = PaymentStatus.COMPLETED

            payment.save()
            send_confirmation_email.delay(
                self.request.user.email, f"Payment:{tx_ref} successful")

            return Response({"message": "Payment successful"})
        else:
            payment.status = PaymentStatus.FAILED
            payment.save()
            return Response({"message": "Payment failed or incomplete"},
                            status=400)
