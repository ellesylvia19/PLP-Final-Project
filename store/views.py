import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product, CartItem
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Create your views here.

def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)

def deal(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/deals.html', context)


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)
    context = {
        'product': product,
        'related_products': related_products,

    }
    return render(request, 'store/detail.html', context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    categories = Category.objects.filter(is_active=True)
    context = {
        'category': category,
        'products': products,
        'categories': categories,
    }
    return render(request, 'store/category_products.html', context)


# Authentication Starts Here


class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
            return redirect('store:home')  # Redirect to the home page after registration
        return render(request, 'account/register.html', {'form': form})
        

@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    # If the item already exists in the cart, increase its quantity
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Product added to cart successfully.")
    return redirect('store:product-detail', slug=slug)

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    return render(request, 'store/cart.html', {'cart_items': cart_items})


@login_required
def checkout(request):
    user = request.user
    address_id = request.GET.get('address')
    
    address = get_object_or_404(Address, id=address_id)
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
        # And Deleting from Cart
        c.delete()
    return redirect('store:orders')


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})


@login_required
def checkout(request):
    if request.method == 'GET':
        address_id = request.GET.get('address')
        
        if not address_id:
            messages.error(request, "Please select a shipping address.")
            #return redirect('store:checkout')
        
        #address = get_object_or_404(Address, id=address_id)
        user = request.user
        
        # Get the user's cart
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Create orders for each item in the cart
        for cart_item in cart.cartitem_set.all():
            Order.objects.create(
                user=user,
                #address=Address,
                product=cart_item.product,
                quantity=cart_item.quantity
            )
        
        # Clear the user's cart after creating orders
        cart.cartitem_set.all().delete()
        
        messages.success(request, "Order placed successfully!")
        return redirect('store:orders')
    else:
        return redirect('store:view-cart')


def shop(request):
    products = Product.objects.all()
    
    context = {
        "products":products
    }
    return render(request, 'store/shop.html', context)
    

def search(request):
    query = request.GET.get('q')

    if query:
        # Perform a case-insensitive search on the product title
        results = Product.objects.filter(title__icontains=query)
    else:
        results = []

    context = {
        'query': query,
        'results': results,
    }

    return render(request, 'store/search.html', context)
