import uuid
from django.db import models

# Create your models here.


class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    host = models.URLField(max_length=200)

    displayName = models.CharField(max_length=70)

    github = models.URLField(max_length=200, unique=True)

    profileImage = models.URLField(max_length=200, unique=True)

    # Max Length: 64 (Username) + 255 (Domain) 
    email = models.EmailField(max_length=320, unique=True)

    username = models.CharField(max_length=30, unique=True)

    