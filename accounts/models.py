from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        READER = "READER", "Reader"
        ADMIN = "ADMIN", "Administrator"

    email = models.EmailField(unique=True)  # BR-01: unique email, used to log in
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.READER)
    contact_number = models.CharField(max_length=20, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"  # matches the SDD table name

    def __str__(self):
        return self.email
