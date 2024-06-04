from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # location = models.CharField(max_length=30, blank=True)
    # birth_date = models.DateField(null=True, blank=True)
    address1 = models.CharField(max_length=50, blank=True)
    address2 = models.CharField(max_length=50, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=30, blank=True)
    postal_code = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=30, blank=True)
    telephone = models.CharField(max_length=30, blank=True)

    slug = models.SlugField(unique=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        super(UserDetails, self).save(*args, **kwargs)

    def __str__(self):
        return f'Details of {self.user}'