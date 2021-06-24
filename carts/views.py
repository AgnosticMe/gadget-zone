from django.shortcuts import render, redirect,get_object_or_404
from .models import Cart, CartItem
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.

# method to get cart id based on session key
def _get_cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id

def add_to_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    
    # if the user is authenticated
    if current_user.is_authenticated:
        product_variation = []

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if  cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            
            existing_variation_list = []
            cart_id_list = []
            for item in cart_item:
                existing_variation = list(item.variation.all())
                existing_variation_list.append(existing_variation)
                cart_id_list.append(item.id)

            if product_variation in existing_variation_list:
                variation_index = existing_variation_list.index(product_variation)
                item_id = cart_id_list[variation_index]
                item = CartItem.objects.get(product=product,  id=item_id)
                item.quantity += 1
                item.save()
            else:
                cart_item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    cart_item.variation.clear()           
                    cart_item.variation.add(*product_variation)
                
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, quantity=1, user=current_user)
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)

            cart_item.save()

        return redirect('carts:cart')

    # if the user is not authenticated
    else:   
        product_variation = []

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        try:
            # get cart using the cart id present in the session
            cart = Cart.objects.get(cart_id=_get_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id = _get_cart_id(request))

        cart.save()

        cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

        if  cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            
            existing_variation_list = []
            cart_id_list = []
            for item in cart_item:
                existing_variation = list(item.variation.all())
                existing_variation_list.append(existing_variation)
                cart_id_list.append(item.id)

            if product_variation in existing_variation_list:
                variation_index = existing_variation_list.index(product_variation)
                item_id = cart_id_list[variation_index]
                item = CartItem.objects.get(product=product, cart=cart, id=item_id)
                item.quantity += 1
                item.save()
            else:
                cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    cart_item.variation.clear()           
                    cart_item.variation.add(*product_variation)
                
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)

            cart_item.save()

        return redirect('carts:cart')


def  remove_from_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _get_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    
    except:
        pass

    return redirect('carts:cart')


def delete_cart_item(request, product_id, cart_item_id):
    cart = cart = Cart.objects.get(cart_id = _get_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    cart_item.delete()
    return redirect('carts:cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _get_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (5 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total' : grand_total,
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='accounts:login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id = _get_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (5 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total' : grand_total,
    }
    return render(request, 'store/checkout.html', context)