from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone



class Author(models.Model):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Discount(models.Model):
    active = models.BooleanField(default=True)
    percentage = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.percentage} % - {self.active}"

class Bonus(models.Model):
    active = models.BooleanField(default=True)
    amount = models.PositiveIntegerField()
    minimum = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.amount} / {self.minimum}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    author = models.ForeignKey(Author, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    bonus = models.ForeignKey(Bonus, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user)
        super(Cart, self).save(*args, **kwargs)

    def __str__(self):
        return f"Cart of {self.user.username}"
    
class CartItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('Regular', 'Regular'),
        ('Bonus', 'Bonus'),
    ]
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, default='Regular')

    def __str__(self):
        return f"{self.cart.user.username}'s Cart | {self.quantity} x {self.product.name}"



class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
    ]
    slug = models.SlugField(unique=True, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    address = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def save(self, *args, **kwargs):
            self.slug = slugify( f"Order {self.id} by {self.user.username}" )
            super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('Regular', 'Regular'),
        ('Bonus', 'Bonus'),
    ]
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    rr_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, default='Regular')
    ## for handling bonus
    bonus_minimum = models.PositiveIntegerField(default=9999999)
    bonus_amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.order.id} | {self.quantity} | {self.rr_quantity} x {self.product.name} @ {self.price} each"



