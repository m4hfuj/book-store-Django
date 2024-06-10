from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import ReturnRequest
from store.models import Inventory, OrderItem, Order, Product, Author, Discount, Bonus
from accounts.models import UserDetails
from django.utils.text import slugify
# from .forms import ProductForm

user = get_user_model()


@login_required
def users_view(request):
    if request.user.is_superuser:
        users = User.objects.all()

        users_serialized = []
        for user in users:
            user_details = UserDetails.objects.get(user=user)
            # print(user_details.mobile)
            serialized = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'address': user_details.address1,
                'mobile': user_details.mobile,
            }
            users_serialized.append(serialized)

        print(users_serialized)
        return render(request, 'admin_panel/users_list.html', {
            'users': users,
            'users_serialized': users_serialized,
        })
    else:
        return JsonResponse({"message":"You are not authorized to view this page"}, status=401)


@login_required
def product_list(request):
    if request.user.is_superuser:
        products = Product.objects.all().select_related('inventory').order_by('name')

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

        return render(request, 'admin_panel/product_list.html', {
            'products_serialized': products_serialized,
        })

@login_required
def product_create(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            product_name = request.POST.get('product_name')
            product_price = request.POST.get('product_price')
            product_author = request.POST.get('author')
            product_quantity = request.POST.get('product_quantity')

            author = Author.objects.get(name = product_author)

            product = Product.objects.create(
                name = product_name,
                price = product_price,
                author = author,
            )

            Inventory.objects.create(
                product=product,
                quantity=product_quantity,
            )

            print(product_name, product_price, product_author, product_quantity)
            return JsonResponse({"message":"Product Added"})

        authors = Author.objects.all().order_by('name')
        return render(request, 'admin_panel/product_create.html', {
            'authors': authors,
        })
    
@login_required
def product_update(request, slug):
    if request.user.is_superuser:
        product = get_object_or_404(Product, slug = slug)
        inventory = get_object_or_404(Inventory, product = product)
        categories = Author.objects.all()
        discounts = Discount.objects.all()
        bonuses = Bonus.objects.all()

        if request.method == 'POST':
            # Extract data from the POST request
            product.name = request.POST.get('name')
            product.price = request.POST.get('price')
            product.author = request.POST.get('author')
            product.discount = request.POST.get('discount')
            product.quantity = request.POST.get('quantity')
            product.bonus = request.POST.get('bonus')

            return redirect('product_list')

        # else:
            # form = ProductForm(instance = product)
        return render(request, 'admin_panel/product_update.html', {
            'product': product,
            'inventory': inventory,
            'categories': categories,
            'discounts': discounts,
            'bonuses': bonuses,
        })

    
    
@login_required
def author_create(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            author_name = request.POST.get('author_name')
            author_description = request.POST.get('author_description')
            try:
                author = Author.objects.create(
                    name = author_name,
                    description = author_description,
                )
            except Exception as e:
                return JsonResponse({"message":str(e)})    
            # print(author_name, author_description)
            return JsonResponse({"message":"Author Added"})
        return render(request, 'admin_panel/author_create.html')


@login_required
def return_requests(request):
    if request.user.is_superuser:
        return_requests = ReturnRequest.objects.all().order_by('-created_at')

        return render(request, 'admin_panel/return_requests.html', {
            'return_requests': return_requests
        })
    else:
        return JsonResponse({"message":"You are not authorized to view this page"}, status=401)
    
@login_required
def rr_accept(request, slug):
    if request.user.is_superuser:
        # Update Request Table
        return_request = ReturnRequest.objects.get(slug=slug)
        return_request.status = 'Accepted'
        return_request.accepted_at = timezone.now()

        # Update inventory Table
        inventory = Inventory.objects.get(product=return_request.order_item.product)
        inventory.quantity += (return_request.quantity + return_request.bonus_return)
        return_request.save()
        inventory.save()

        # Update order table
        order_item = return_request.order_item
        order_item.rr_quantity -= return_request.quantity
        order_item.save()
        
        # Update rr of bonus order item
        order_items = order_item.order.items.all()
        for bonus_item in order_items:
            if bonus_item.product == order_item.product and bonus_item.type == "Bonus":
                if bonus_item.rr_quantity - return_request.bonus_return >= 0:
                    bonus_item.rr_quantity -= return_request.bonus_return
                    bonus_item.save()

        return redirect('return_requests')
    else:
        return JsonResponse("You are not authorized to view this page")

@login_required
def rr_reject(request, slug):
    if request.user.is_superuser:
        return_request = ReturnRequest.objects.get(slug=slug)
        return_request.status = 'Rejected'
        return_request.rejected_at = timezone.now()

        order_item = return_request.order_item
        order_item.quantity += return_request.quantity

        return_request.save()
        order_item.save()

        # Update rr of bonus order item
        order_items = order_item.order.items.all()
        for bonus_item in order_items:
            if bonus_item.product == order_item.product and bonus_item.type == "Bonus":
                # if bonus_item.rr_quantity - return_request.bonus_return >= 0:
                bonus_item.quantity += return_request.bonus_return
                bonus_item.save()

        return redirect('return_requests')
    else:
        return JsonResponse("You are not authorized to view this page")
    


@login_required
def all_order_history(request):
    if request.user.is_superuser:
        orders = Order.objects.all().order_by('-created_at')

        item_sets = []
        for order in orders:
            items = OrderItem.objects.filter(order=order)
            item_sets.append(items)

        order_item_sets = zip(orders, item_sets)

        return render(request, 'admin_panel/order_list.html', {
            'order_item_sets': order_item_sets
        })

    else:
        return JsonResponse({"message":"You are not authorized to view this page"}, status=401)


@login_required
def deliver_product(request, slug):
    if request.user.is_superuser:
        order = Order.objects.get(slug=slug)
        order.status = 'Delivered'
        # order.delivered_at = timezone.now()
        order.save()
        return redirect('all_order_history')
    else:
        return JsonResponse({"message":"You are not authorized to view this page"}, status=401)
