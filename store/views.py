from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponse, JsonResponse

from .models import Product, Inventory, Cart, CartItem, Order, OrderItem
from accounts.models import UserDetails
from admin_panel.models import ReturnRequest
from django.contrib import messages
import json


def store_view(request):
    sort_by = request.GET.get('sort_by', 'name')  # Default sort by name
    sort_order = request.GET.get('sort_order', 'asc')  # Default sort order ascending

    if sort_order == 'desc':
        sort_by = f'-{sort_by}'

    products = Product.objects.all().select_related('inventory').order_by(sort_by)

    # json serialize
    products_serialized = []
    for product in products:
        serialized_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': product.inventory.quantity,
            'slug': product.slug
        }
        # Check if product has author, otherwise set author to None
        if product.author:
            serialized_product['author'] = product.author.name
        else:
            serialized_product['author'] = None
        # Check if product has discount, otherwise set discount_active and discount to False and None respectively
        if product.discount:
            serialized_product['discount_active'] = product.discount.active
            serialized_product['discount'] = product.discount.percentage
        else:
            serialized_product['discount_active'] = False
            serialized_product['discount'] = None
        # Check if product has bonus
        if product.bonus:
            serialized_product['bonus_active'] = product.bonus.active
            serialized_product['bonus_amount'] = product.bonus.amount
            serialized_product['bonus_minimum'] = product.bonus.minimum
        else:
            serialized_product['bonus_active'] = False
            serialized_product['bonus_amount'] = None
            serialized_product['bonus_minimum'] = None

        products_serialized.append(serialized_product)

    return render(request, 'store/store-front.html', {
        'products_serialized': products_serialized,
    })


# @login_required
def add_to_cart(request, slug):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
        # return redirect('login')
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, slug=slug)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    inventory = Inventory.objects.get(product=cart_item.product)

    if request.method == 'POST':
        amount = int(request.POST.get('amount'))

    if amount < inventory.quantity:
        cart_item.quantity += amount
        if cart_item.quantity > inventory.quantity:
            return JsonResponse({'error': f'Already equal to stock for {cart_item.product.name}'}, status=400)
    else:
        return JsonResponse({'error': f'Not enough in stock for {cart_item.product.name}'}, status=400)

    cart_item.save()
    # return redirect('store-front')
    return JsonResponse({'success': f'Added {amount} of {product.name} to cart successfully!'})

@login_required
def remove_from_cart(request, slug):
    cart = get_object_or_404(Cart, user=request.user)
    product = Product.objects.get(slug=slug)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart-view')


######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
@login_required
def checkout(request):
    user = request.user
    user_address = get_object_or_404(UserDetails, user=user).address1
    cart = get_object_or_404(Cart, user=user)
    cart_items = cart.items.all()

    cart_items_serialized = []
    for item in cart_items:
        serialized = {
            'id': item.id,
            'name': item.product.name,
            # 'author': item.product.author.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'slug': item.product.slug,
        }
        # Check if product has author, otherwise set author to None
        if item.product.author:
            serialized['author'] = item.product.author.name
        else:
            serialized['author'] = None
        # Check if product has discount, otherwise set discount_active and discount to False and None respectively
        if item.product.discount:
            serialized['discount_active'] = item.product.discount.active
            serialized['discount'] = item.product.discount.percentage
            # serialized['price'] = ( item.product.price * (100-item.product.discount.percentage)/100 )
        else:
            serialized['discount_active'] = False
            serialized['discount'] = None
        # Check for bonus
        if item.product.bonus:
            serialized['bonus_active'] = item.product.bonus.active
            serialized['bonus_amount'] = item.product.bonus.amount
            serialized['bonus_minimum'] = item.product.bonus.minimum
        else:
            serialized['bonus_active'] = False
            serialized['bonus_amount'] = None
            serialized['bonus_minimum'] = None

        cart_items_serialized.append(serialized)

    total_price = 0.0
    # for item in cart_items:
    #     total_price += float(item.product.price * item.quantity)
    if request.method == 'POST':
        address = request.POST.get('address')
        if not address:
            return HttpResponse("Address is required", status=400)

        # Create the order
        order = Order.objects.create(
            user=user,
            address=address,
            total_price=total_price,  # Will update later
        )

        for item in cart_items:
            product = item.product
            quantity = item.quantity

            # Check inventory
            inventory = get_object_or_404(Inventory, product=product)
            if inventory.quantity < quantity:
                return HttpResponse(f"Not enough inventory for {product.name}", status=400)

            # Update price in discounted
            new_price = item.product.price
            if item.product.discount:
                if item.product.discount.active:
                    new_price = ( item.product.price * (100-item.product.discount.percentage)/100 )

            # Here goes the check for bonus product
            # bonus_product = 
            # if item.type == 

            # Create OrderItem
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                rr_quantity=quantity,
                price=new_price,
            )
            # Update inventory
            inventory.quantity -= quantity
            # print(inventory.quantity, quantity)
            inventory.save()

        total_price = request.POST.get('total-price-form')

        # Here goes the check for bonus product
        for item in cart_items:
            product = item.product
            quantity = item.quantity

            # Check inventory
            inventory = get_object_or_404(Inventory, product=product)
            if inventory.quantity < quantity:
                return HttpResponse(f"Not enough inventory for {product.name}", status=400)
            
            if product.bonus:
                if product.bonus.active:
                    bonus_quantity = product.bonus.amount * ( quantity // product.bonus.minimum)
                    # print("Here", bonus_quantity)
                    messages.success(request, f"You got {bonus_quantity} bonus {product.name}")

                    # Create OrderItem
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=bonus_quantity,
                        rr_quantity=bonus_quantity,
                        price=0.0,
                        type="Bonus",
                        bonus_minimum=product.bonus.minimum,
                        bonus_amount=product.bonus.amount,
                    )
                    # Update inventory
                    inventory.quantity -= bonus_quantity
                    # print(inventory.quantity, quantity)
                    inventory.save()

        # Update order total price
        order.total_price = total_price
        order.save()

        # Clear the cart
        cart.items.all().delete()

        # messages.success(request, 'Your order has been placed successfully!')
        return redirect('order-history')

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'cart_items_serialized': cart_items_serialized,
        # 'total_price': total_price
        'user_address': user_address,
    })



@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    item_sets = []
    for order in orders:
        items = OrderItem.objects.filter(order=order)
        item_sets.append(items)

    order_item_sets = zip(orders, item_sets)

    return render(request, 'store/order-history.html', {
        'order_item_sets': order_item_sets
    })


@login_required
def cancel_order(request, slug):
    order = get_object_or_404(Order, slug=slug)
    
    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        inventory = Inventory.objects.get(product=item.product)
        inventory.quantity += item.quantity
        inventory.save()
        
    order.status = 'Cancelled'
    order.save()

    messages.error(request, 'Your order has been canceled!')
    return redirect('order-history')


@login_required
def re_order(request, slug):
    order = get_object_or_404(Order, slug=slug)
    
    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        inventory = Inventory.objects.get(product=item.product)
        inventory.quantity -= item.quantity
        inventory.save()
        
    order.status = 'Pending'
    order.save()

    messages.success(request, 'Your order has been Re eshtablished!')
    return redirect('order-history')


@login_required
def make_return_request(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    items_serialized = []
    for order in orders:
        if order.status == "Delivered":
            items = OrderItem.objects.filter(order=order)
            # print(items)

            for item in items:
                if item.type != "Bonus":

                    bonus_item = None
                    for i in items:
                        if i.product == item.product and i.type == "Bonus":
                            bonus_item = i
                            print(bonus_item)

                    serialized = {
                        'id': item.id,
                        'name': item.product.name,
                        'quantity': item.quantity,
                        'rr_quantity': item.rr_quantity,
                        'bonus': 0,
                        'rr_bonus': 0,
                        'price': item.price,
                        'created': order.created_at,
                        # 'status': status,
                    }
                    if bonus_item:
                        serialized['bonus'] = ((item.quantity // bonus_item.bonus_minimum) * bonus_item.bonus_amount)
                        serialized['rr_bonus'] = ((item.rr_quantity // bonus_item.bonus_minimum) * bonus_item.bonus_amount)

                    items_serialized.append(serialized)

    return render(request, 'store/make-return-request.html', {
        'items_serialized': items_serialized
    })

@login_required
def make_return_request__item_id(request, pk):
    if request.method == "POST":
        # refund_bonus_q = 0
        quantity = int( request.POST.get('amount') )
        item = OrderItem.objects.get(id=pk)
        order = item.order
        order_items = order.items.all()

        refund_bonus_q = 0
        for bonus_item in order_items:
            if bonus_item.product == item.product and bonus_item.type == "Bonus":
                refund_bonus_q = bonus_item.quantity - ( ((item.quantity - quantity)// bonus_item.bonus_minimum) * bonus_item.bonus_amount )
                print("###############################################################################")
                # print(refund_bonus_q, bonus_item.quantity, item.quantity, quantity)
                print(bonus_item.quantity)
                print("###############################################################################")
                if refund_bonus_q > 0:
                    bonus_item.quantity -= refund_bonus_q
                    bonus_item.save()

        price_refund = item.price * quantity
        return_request = ReturnRequest.objects.create(
            user = request.user,
            order_item = item,
            quantity = quantity,
            bonus_return = refund_bonus_q,
            status = "Pending",
            price_refund = price_refund,
        )
        # Update only OrderItem table so that user cant make further request of same item
        item.quantity -= quantity

        return_request.save()
        item.save()
        # print(f"{order.items.all()}")

        return HttpResponse(f"{order}")

    return HttpResponse('Failed')


@login_required
def my_return_requests(request):
    return_requests = ReturnRequest.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'store/my-return-request.html', {
        'return_requests': return_requests
    })  

