from django.contrib import auth, messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Account, UserProfile
from .forms import RegistrationForm, UserProfileForm, UserForm
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderProduct

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart, CartItem

import requests
from urllib.parse import urlparse


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string(
                'accounts/account_verification_email.html',
                {
                    'user': user,
                    'domain': current_site.domain,
                    # 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                }
            )

            to_email = email
            send_email = EmailMessage(
                mail_subject,
                message,
                to=[to_email]
            )
            send_email.send()

            # messages.success(request, 'Thank you for registering with us. We have sent you a verification email to your email address. Please verify it.')
            # return redirect('register')
            return redirect('/accounts/login/?command=verification&email='+email)

    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)


                    # Getting the product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # Get the cart items from the users to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                            
                    for item in cart_item:
                        existing_variations = item.variations.all()
                        ex_var_list.append(list(existing_variations))
                        id.append(item.id)

                    # product_variation = [1, 2, 3, 4, 5]
                    # ex_var_list = [5, 3, 5, 4]
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()

                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in.')


            url = request.META.get('HTTP_REFERER')
            try:
                query = urlparse(url).query
                print('query -> ', query)
                print('-------')

                #next = /cart/checkout/
                params = dict(x.split('=') for x in query.split('&') if '=' in x)
                print('params', params)

                if 'next' in params:
                    return redirect(params['next'])
                else:
                    return redirect('home')   # or 'home'
                
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
        
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Congratulations! Your account has been activated.')
        return redirect('login')

    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')
    

# @login_required(login_url = 'login')
# def dashboard(request):
#     orders = Order.objects.filter(
#         user_id=request.user,
#         is_ordered=True
#     ).order_by('-created_at')

#     orders_count = orders.count()

#     userprofile = UserProfile.objects.get(user_id=request.id)

#     context = {
#         'orders_count': orders_count,
#         'userprofile': userprofile,
#     }
#     return render(request, 'accounts/dashboard.html', context)
@login_required(login_url='login')
def dashboard(request):

    orders = Order.objects.filter(
        user=request.user,
        is_ordered=True
    ).order_by('-created_at')

    orders_count = orders.count()

    userprofile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }

    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']

        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset Password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password!'
            message = render_to_string(
                'accounts/reset_password_email.html',
                {
                    'user': user,
                    'domain': current_site.domain,
                    'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                      'token': default_token_generator.make_token(user),
                }
            )
            
            to_email = email
            send_email = EmailMessage(
                mail_subject,
                message,
                to=[to_email]
            )
            send_email.send()

            messages.success(request, 'Password request has been sent to your email address!')
            return redirect('login')

        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')

    else:
        messages.error(request, 'This link is expired!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset successful!')
            return redirect('login')


        else:
            messages.error(request, 'Password did not match!')
            return redirect('resetPassword')
    else:  
        return render(request, 'accounts/resetPassword.html')

@login_required(login_url='/login/')
def my_order(request):
    orders = Order.objects.filter(
        user=request.user,
        is_ordered=True
    ).order_by('-created_at')

    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_order.html', context)

@login_required(login_url='/login/')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        user_profile = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and user_profile.is_valid():
            user_form.save()
            user_profile.save()
            messages.success(request, "Your profile has been upated!")
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        user_profile = UserProfileForm(instance=userprofile)

        context = {
            'user_form': user_form,
            'user_profile': user_profile,
            'userprofile': userprofile,
        }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect('change_password')

        # Check current password
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('change_password')

        # Prevent using the same password
        if current_password == new_password:
            messages.error(request, "Your new password must be different from your current password.")
            return redirect('change_password')

        # Save the new password
        user.set_password(new_password)
        user.save()

        # Log the user out
        logout(request)

        messages.success(request, "Your password has been changed successfully. Please log in again.")
        return redirect('login')

    return render(request, 'accounts/change_password.html')


def order_details(request, order_id):
    order_details = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_details:
        subtotal += i.product_price * i.quantity
        

    context = {
        'order_details': order_details,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_details.html', context)