from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime


# Create your views here.
def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        order = {'get_total_items': 0, 'get_cart_total': 0}

    products = Product.objects.all()
    context = {
        'products': products,
        'order': order,
    }
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()
    else:
        orderitems = []
        order = {'get_total_items': 0, 'get_cart_total': 0}

        cart =request.COOKIES['cart']



    context = {
        'order': order,
        'orderitems': orderitems,

    }
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderitems = order.orderitem_set.all()
    else:
        orderitems = []
        order = {'get_total_items': 0, 'get_cart_total': 0}

    context = {
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['product_id']
    action = data['action']
    order, created = Order.objects.get_or_create(customer=request.user.customer, complete=False)
    product = Product.objects.get(id=product_id)

    orderitems, created = OrderItem.objects.get_or_create(product=product, order=order)

    if action == 'add':
        orderitems.quantity = orderitems.quantity + 1
    elif action == 'remove':
        orderitems.quantity = orderitems.quantity - 1
    orderitems.save()

    if orderitems.quantity <= 0:
        orderitems.delete()

    return JsonResponse("Item Added", safe=False)


def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    userInfo = data['form']
    shippingInfo = data['shipping']

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        if userInfo['total'] == str(order.get_cart_total):
            print("*")
            order.transaction_id = transaction_id
            order.complete = True
        order.save()

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=shippingInfo['address'],
            city=shippingInfo['city'],
            state=shippingInfo['state'],
            zipcode=shippingInfo['zipcode'],
            country=shippingInfo['country'],
        )

    return JsonResponse("Order Completed!", safe=False)
