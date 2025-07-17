import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from listings.models import Listing, Booking, Review, Payment, Users
from listings.models import (
    UserRole,
    BookingStatus,
    PaymentMethod,
    PaymentStatus,
)


class Command(BaseCommand):
    """seed db with sample data"""

    def handle(self, *args, **options):
        self.stdout.write("SEEDING...")

        # delete existing data
        Users.objects.all().delete()
        Listing.objects.all().delete()
        Booking.objects.all().delete()
        Review.objects.all().delete()
        Payment.objects.all().delete()

        # create
        hosts = []

        for i in range(1, 6):
            host = Users.objects.create_user(
                username=f"host{i}",
                email=f"host{i}@example.com",
                password="hostpass123",
                role=UserRole.HOST.value,
            )
            hosts.append(host)
            self.stdout.write(
                f"Created host: {host.username} with ID {host.id}"
            )

        guests = []
        for i in range(1, 11):
            guest = Users.objects.create_user(
                username=f"guest{i}",
                email=f"guest{i}@example.com",
                password="guestpass123",
                role=UserRole.CUSTOMER.value,
            )
            guests.append(guest)
            self.stdout.write(
                f"Created guest: {guest.username} with ID {guest.id}"
            )
        # Create properties
        locations = ["New York", "Los Angeles", "Chicago", "Miami", "Seattle"]
        properties = []
        for i, host in enumerate(hosts):
            for j in range(2):  # Each host has 2 properties
                property = Listing.objects.create(
                    title=f"Beautiful apartment in {locations[i]}",
                    description=(
                        f"Spacious {random.randint(1, 4)}"
                        f"bedroom apartment in the heart of {locations[i]}"
                    ),
                    price_per_night=random.randint(50, 200),
                    host=host,
                    location=locations[i],
                    bedrooms=random.randint(1, 4),
                    bathrooms=random.randint(1, 3),
                    max_guests=random.randint(2, 8),
                    amenities="WiFi, Kitchen, TV, Air Conditioning",
                )
                properties.append(property)
                self.stdout.write(
                    f"Created property: {property.title} with ID {property.id}"
                )

        # create bookings for random properties
        bookings = []
        status_choices = [s.value for s in BookingStatus]
        for i in range(20):
            property = random.choice(properties)
            guest = random.choice(guests)
            check_in = datetime.now() + timedelta(days=random.randint(1, 30))
            check_out = check_in + timedelta(days=random.randint(1, 14))
            total_price = (
                check_out - check_in
            ).days * property.price_per_night

            booking = Booking.objects.create(
                property=property,
                guest=guest,
                check_in_date=check_in,
                check_out_date=check_out,
                total_price=total_price,
                status=random.choice(status_choices),
            )
            bookings.append(booking)
            self.stdout.write(
                f"Created booking ID {booking.id}"
                f"for {guest.username} at {property.title}"
            )
            # Create reviews
            for i in range(15):
                property = random.choice(properties)
                guest = random.choice(guests)

                review = Review.objects.create(
                    property=property,
                    author=guest,
                    rating=random.randint(1, 5),
                    comment=(
                        f"My stay at {property.title} was"
                        f'{"great" if random.random() > 0.3 else "okay"}.'
                    ),
                )
                self.stdout.write(
                    f"Created review ID {review.id} by"
                    f"{guest.username} for {property.title}"
                )

            # Create payments
            payment_methods = [m.value for m in PaymentMethod]
            # payment_statuses = [s.value for s in PaymentStatus]
            for booking in bookings:
                if booking.status in [
                    BookingStatus.CONFIRMED.value,
                    BookingStatus.COMPLETED.value,
                ]:
                    payment = Payment.objects.create(
                        booking=booking,
                        amount=booking.total_price,
                        payment_method=random.choice(payment_methods),
                        status=(
                            PaymentStatus.COMPLETED.value
                            if booking.status == BookingStatus.COMPLETED.value
                            else PaymentStatus.PENDING.value
                        ),
                        transaction_date=datetime.now()
                        - timedelta(days=random.randint(1, 10)),
                    )
                    self.stdout.write(
                        f"Created payment ID {payment.id}"
                        f"for booking #{booking.id}"
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully seeded database with explicit Enums!"
                )
            )
