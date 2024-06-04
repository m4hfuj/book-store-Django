from django.contrib import admin
from .models import Author, Product, Inventory, Cart, CartItem, Order, OrderItem, Discount, Bonus
#, ItemType
# ReturnRequest
#, ShippingAddress, Payment

admin.site.register(Author)
admin.site.register(Discount)
admin.site.register(Bonus)
admin.site.register(Product)
admin.site.register(Inventory)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)

# admin.site.register(ItemType)

# admin.site.register(ReturnRequest)
# admin.site.register(ShippingAddress)
# admin.site.register(Payment)
