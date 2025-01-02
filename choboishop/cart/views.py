from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from choboionline.models import Product
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    """
    Add a product to the cart or update its quantity.

    Args:
        request: The HTTP request object.
        product_id (int): The ID of the product to add.

    Returns:
        HttpResponseRedirect: Redirect to the cart detail page.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    """
    Remove a product from the cart.

    Args:
        request: The HTTP request object.
        product_id (int): The ID of the product to remove.

    Returns:
        HttpResponseRedirect: Redirect to the cart detail page.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    """
    Display the details of the cart.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Rendered HTML page with cart details.
    """
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'override': True}
        )
    return render(request, 'cart/detail.html', {'cart': cart})
