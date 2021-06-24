import accounts
from email.message import EmailMessage
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from . models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# imports for email verificatio
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponse

from carts.models import Cart, CartItem
from carts.views import _get_cart_id
import requests


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email,  password=password)
            user.phone_number = phone_number
            user.save()
            
            # User Activation
            current_site = get_current_site(request)
            mail_subject = "Confirm the activation of your account."
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

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
                cart = Cart.objects.get(cart_id=_get_cart_id(request))
                cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    # getting the product variation by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = list(item.variation.all())
                        product_variation.append(variation)
                    
                    # get the cart items from the user to access his porduct variation
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variation_list = []
                    cart_id_list = []
                    for item in cart_item:
                        existing_variation = list(item.variation.all())
                        existing_variation_list.append(existing_variation)
                        cart_id_list.append(item.id)

                    for product_variant in product_variation:
                        if product_variant in existing_variation_list:
                            variation_index = existing_variation_list.index(product_variant)
                            item_id = cart_id_list[variation_index]
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
            messages.success(request, "Logged in Successfully")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('accounts:dashboard')
        else:
            messages.error(request, "Invalid login Credentials")
            return redirect('accounts:login')

    return render(request, 'accounts/login.html')

@login_required(login_url='accounts:login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Logged out Successfully")
    return redirect('accounts:login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is verified and activated.")
        return redirect('accounts:login')
    else:
        messages.error(request, "Invalid activation link")
        return redirect('accounts:register')


@login_required(login_url='accounts:login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')
    

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # reset password email
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, "Reset password email sent successfully!")
            return redirect('accounts:login')
        else:
            messages.error(request, "Account does not exist")
            return redirect('accounts:forgot_password')

    return render(request, 'accounts/forgot_password.html')


def reset_passwordValidation(request, uidb64, token ):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Setup the new password for your account.")
        return redirect('accounts:reset_password')
    else:
        messages.error(request, "Invalid/Expired link")
        return redirect('accounts:forgot_password')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset Successful!')
            return redirect('accounts:login')
        else:
            messages.error(request, "Passwords doesn't match")
            return redirect('accounts:reset_password')

    else:
        return render(request, 'accounts/reset_password.html')

