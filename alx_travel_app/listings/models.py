import uuid
import enum
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy

# Create your models here.


class UserRole(str, enum.Enum):
    HOST = "HOST"
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"

    @classmethod
    def choices(cls):
        return tuple((item.value, item.name) for item in cls)


class Users(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(blank=False, max_length=60)
    last_name = models.CharField(blank=False, max_length=60)
    phone_number = models.CharField(blank=False, max_length=13)
    password = models.CharField(gettext_lazy("password"), max_length=128)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=8,
        choices=UserRole.choices(),
        default=UserRole.CUSTOMER.value,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"USER:{self.username} ROLE:({self.role})"


class Listing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    host = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="listings"
    )
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Additional fields
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    max_guests = models.PositiveIntegerField()
    amenities = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} in {self.location}"


class BookingStatus(enum.Enum):
    PAYMENT_PENDING = "PAYMENT_PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

    @classmethod
    def choices(cls):
        return tuple((item.value, item.name) for item in cls)


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    guest = models.ForeignKey(Users, on_delete=models.CASCADE)
    check_in_date = models.DateTimeField()
    check_out_date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices(),
        default=BookingStatus.PAYMENT_PENDING,
    )

    def __str__(self):
        return f"Booking #{self.id} for {self.listing.title}"


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="reviews"
    )
    author = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.author.username} for {self.listing.title}"


class PaymentMethod(enum.Enum):
    CARD = "CARD"
    PAYPAL = "PAYPAL"
    MOBILE_MONEY = "MOBILE MONEY"

    @classmethod
    def choices(cls):
        return tuple((item.value, item.name) for item in cls)


class PaymentStatus(enum.Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    REFUNDED = "REFUNDED"

    @classmethod
    def choices(cls):
        return tuple((item.value, item.name) for item in cls)


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="payment"
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    payment_method = models.CharField(
        max_length=15,
        choices=PaymentMethod.choices(),
        default=PaymentMethod.CARD,
    )
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices(),
        default=PaymentStatus.PENDING,
    )
