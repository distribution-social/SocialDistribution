import uuid
from django.db import models

# Create your models here.


class Author(models.Model):
    # Unique ID of the user
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    # Server host of the user
    host = models.URLField(max_length=200)

    # Max Length: 35 (First Name) + 35 (Last Name)
    displayName = models.CharField(max_length=70)

    github = models.URLField(max_length=200, unique=True)

    profileImage = models.URLField(max_length=200, unique=True)

    # Max Length: 64 (Username) + 255 (Domain)
    email = models.EmailField(max_length=320, unique=True)

    username = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f"{self.displayName} ({self.id})"
