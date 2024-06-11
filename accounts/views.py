# accounts/views.py
from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from .models import UserDetails
from store.models import Cart
from django.contrib.auth.decorators import login_required

# class SignUpView(CreateView):
#     form_class = CustomUserCreationForm
#     success_url = reverse_lazy("login")
#     template_name = "registration/signup.html"


def check_username(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            if User.objects.filter(username = username):
                return JsonResponse({'error': 'Username already exists'}, status=400)
            else:
                print("Alright==================================================================")
                return JsonResponse({'success': 'Procced with registration.'}, status=200)
        else:
            return JsonResponse({'error': 'Username is required'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        address1 = request.POST.get('address1')
        mobile = request.POST.get('mobile')

        if form.is_valid():
            # pass
            user = form.save()

            # Create user details
            user_details = UserDetails.objects.create(
                user=user,
                address1=str(address1),
                mobile=str(mobile),
            )
            user_details.save()

            # Create a cart
            cart = Cart.objects.create(
                user=user,
            )
            cart.save()

            # Log the user in and redirect to the success URL
            login(request, user)
            return redirect(reverse_lazy('login'))
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def user_details(request):
    user = request.user
    user_details = UserDetails.objects.get(user = user)
    return render(request, 'accounts/user_details.html', {
       'user_details': user_details,
       'user': user,
    }) 