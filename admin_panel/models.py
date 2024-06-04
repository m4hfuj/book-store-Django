from django.db import models
from django.utils.text import slugify
from django.utils import timezone

from django.contrib.auth.models import User
from store.models import OrderItem


class ReturnRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    bonus_return = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    price_refund = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='accepted_by')
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='rejected_by')

    def save(self, *args, **kwargs):
        # created_at_str = str()
        self.slug = slugify(f"{self.quantity}x{self.order_item.product.name} by {self.user.username} {self.created_at}")
        super(ReturnRequest, self).save(*args, **kwargs)

    def __str__(self):
        return f"Return Request for {self.quantity} x {self.order_item.product.name} by {self.user.username}"

