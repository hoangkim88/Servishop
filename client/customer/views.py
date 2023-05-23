import requests
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponseRedirect
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def register(request):
    if request.method == 'POST':
        url = 'http://localhost:5001/register'  # Update with the Flask server URL
        data = {
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
            'role': 'user',
        }
        response = requests.post(url, json=data)

        if response.status_code == 201:  # Registration successful
            user_id = response.json().get('user_id')
            username = response.json().get('username')
            request.session['user_id'] = user_id
            request.session['username'] = username
            return redirect('display_products')

        return render(request, 'register.html', {'error': response.json().get('message')})

    return render(request, 'register.html')

def logout(request):
    # Clear the session data
    request.session.clear()
    
    # Redirect the user to the login page or any other desired page
    return redirect('login')

def login(request):
    if request.method == 'POST':
        url = 'http://localhost:5001/login'  # Update with the Flask server URL
        data = {
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
        }
        response = requests.post(url, json=data)

        if response.status_code == 200:  # Login successful
            user_id = response.json().get('user_id')
            username = response.json().get('username')
            request.session['user_id'] = user_id
            request.session['username'] = username
            return redirect('display_products')

        return render(request, 'login.html', {'error': response.json().get('message')})

    return render(request, 'login.html')

def display_products(request):
    url = 'http://localhost:5002/products'  # Update with the Flask server URL
    response = requests.get(url)
    products = response.json()

    # Fetch all categories
    categories = get_all_categories()

    return render(request, 'products.html', {'products': products, 'categories': categories})

def get_all_categories():
    # Send a request to the product service to retrieve all products
    response = requests.get('http://localhost:5005/categories')

    if response.status_code == 200:
        # Extract unique categories from products
        categories = response.json()
        return categories
    else:
        return []

def search_by_category(request, category):
    response = requests.get(f'http://localhost:5005/search_by_category?category={category}')

    if response.status_code == 200:
        filtered_products = response.json()
        categories = get_all_categories()
        return render(request, 'products.html', {'products': filtered_products, 'categories': categories})
    else:
        return render(request, 'products.html', {'error': 'Error searching by category'})

def get_product(request, product_id):
    url = f'http://localhost:5002/products/{product_id}'  # Update with the Flask server URL
    response = requests.get(url)

    if response.status_code == 200:
        product = response.json()
        return render(request, 'product_details.html', {'product': product})
    else:
        error_message = 'Product not found'
        return render(request, 'product_details.html', {'error': error_message})

def add_to_cart(request):
    # Retrieve the username from the session
    username = request.session.get('username')

    if not username:
        # Handle the case where the username is not available in the session
        return JsonResponse({'message': 'Username not found in session'}, status=400)

    # Retrieve other data from the request
    product_id = request.POST.get('product_id')
    quantity = 1

    # Make a POST request to the Flask API
    url = 'http://localhost:5003/add_to_cart'
    data = {
        'username': username,
        'product_id': product_id,
        'quantity': quantity
    }
    response = requests.post(url, json=data)

    # Check if the Flask API response is successful
    if response.status_code == 200:
        # Redirect to the 'get_cart' view
        return redirect('cart')
    else:
        # Handle the case where the Flask API response is not successful
        error_message = response.json().get('message')
        return JsonResponse({'message': error_message}, status=400)

def search_by_name(request):
    if request.method == 'GET':
        product_name = request.GET.get('name')

        # Send a request to the Flask server to search by name
        flask_server_url = 'http://localhost:5005'  # Update with the Flask server URL
        search_url = f'{flask_server_url}/search_by_name?name={product_name}'
        response = requests.get(search_url)

        if response.status_code == 200:
            filtered_products = response.json()
            categories = get_all_categories()
            return render(request, 'products.html', {'products': filtered_products, 'categories': categories})
        else:
            return render(request, 'products.html', {'error': 'Error searching by product name'})

    # Render the products.html template without any filtering if the request method is not GET
    categories = get_all_categories()
    return render(request, 'products.html', {'categories': categories})

def filter_by_price(request):
    sort_order = request.GET.get('sort_order')

    # Update with the Flask server URL
    flask_server_url = 'http://localhost:5005'
    filter_url = f'{flask_server_url}/filter_by_price?sort_order={sort_order}'
    
    try:
        response = requests.get(filter_url)
        if response.status_code == 200:
            filtered_products = response.json()

            # Fetch all categories
            categories = get_all_categories()

            return render(request, 'products.html', {'products': filtered_products, 'categories': categories})
        else:
            return render(request, 'products.html', {'error': 'Error filtering by price'})
    except requests.exceptions.RequestException as e:
        return render(request, 'products.html', {'error': 'Error connecting to Flask server'})

def get_cart(request):
    username = request.session.get('username')
    if not username:
        return redirect('login')  # Replace 'login' with the appropriate login URL in your Django project

    url = 'http://localhost:5003/get_cart'  # Update with the Flask server URL
    data = {'username': username}
    response = requests.post(url, json=data)

    if response.status_code == 200:
        cart_items = response.json().get('cart')
        products = []
        total = 0

        for item in cart_items:
            product_id = item['product_id']
            quantity = item['quantity']

            # Retrieve the product details
            product_url = f'http://localhost:5002/products/{product_id}'  # Update with the Flask server URL
            product_response = requests.get(product_url)

            if product_response.status_code == 200:
                product = product_response.json()
                price = product['price']
                subtotal = price * quantity
                total += subtotal

                # Append the product details to the list
                products.append({
                    'product_id': product_id,
                    'name': product['name'],
                    'image': product['image'],
                    'price': price,
                    'quantity': quantity,
                    'subtotal': subtotal
                })
                request.session['cart_items'] = products

        return render(request, 'cart.html', {'products': products, 'total': total})

    return render(request, 'cart.html', {'error': 'Error retrieving cart items'})

def update_cart(request):
    # Retrieve the necessary data from the request
    username = request.session.get('username')
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    # Prepare the data to send to the Flask server
    data = {
        'username': username,
        'product_id': product_id,
        'quantity': quantity
    }

    # Make a POST request to the server
    response = requests.post('http://localhost:5003/update_cart', json=data)

    # Check if the request was successful
    if response.status_code == 200:
        return redirect('cart')  # Redirect to the cart page
    else:
        return JsonResponse({'error': 'Failed to update cart'}, status=response.status_code)
    
def remove_from_cart(request):
    # Retrieve the necessary data from the request
    username = request.session.get('username')
    product_id = request.POST.get('product_id')

    # Prepare the data to send to the Flask server
    data = {
        'username': username,
        'product_id': product_id
    }

    # Make a POST request to the Flask server
    response = requests.post('http://localhost:5003/remove_from_cart', json=data)

    # Check if the request was successful
    if response.status_code == 200:
        return redirect('cart')  # Redirect to the cart page
    else:
        return JsonResponse({'error': 'Failed to remove cartitem'}, status=response.status_code)
    
def stripe_checkout(request):
    # Retrieve cart items from the template context
    cart_items = request.session.get('cart_items', [])
    
    # Create line items for Stripe checkout
    line_items = []
    for item in cart_items:
        line_items.append({
            
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item['name'],
                },
                # Convert price to cents
                "unit_amount": int(item['price']) * 100,

            },
            "quantity": item['quantity'],
 
        })

    # Create Stripe checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        invoice_creation={"enabled": True},
        line_items=line_items,
        mode="payment",
        success_url=settings.STRIPE_SUCCESS_URL + "?status=success" + "&session_id={CHECKOUT_SESSION_ID}",
        cancel_url=settings.STRIPE_CANCEL_URL + "?status=cancel",
    )
    
    # Empty the cart
    request.session['cart_items'] = []
    
    # Return a redirect to the Stripe checkout URL
    return HttpResponseRedirect(session.url)

def stripe_success(request):
    # Check if the checkout was successful
    if request.GET.get('status') == 'success':
        session_id = request.GET.get('session_id')  # Get the Checkout Session ID from the request
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        invoice_id = session.invoice
        invoice = stripe.Invoice.retrieve(invoice_id)
        # Consume the create_order server function
        user_id = request.session.get("user_id")  # Assuming you have a user object with an id
        username = request.session.get("username")
        create_order_payload = {
            'user_id': str(user_id),
            'username': username
        }
        create_order_response = requests.post('http://localhost:5004/create_order', json=create_order_payload)
        
        # Render the success template
        return render(request, 'checkout/success.html', {'invoice_id': invoice_id})
    else:
        # If the checkout was canceled, redirect back to the cart
        return HttpResponseRedirect(reverse('cart'))


def stripe_cancel(request):
    # Check if the checkout was canceled
    if request.GET.get('status') == 'cancel':
        # Render the cancel template
        return render(request, 'checkout/cancelled.html')
    else:
        # If the checkout was successful, redirect to the success view
        return HttpResponseRedirect(reverse('checkout_success'))


def invoice(request, invoice_id):
    invoice = stripe.Invoice.retrieve(invoice_id)
    return render(request, 'checkout/view_invoice.html', {'invoice': invoice})

def get_order(request):
    user_id = request.session.get('user_id')  # Retrieve user_id from session

    flask_server_url = 'http://localhost:5004'  # Replace with the Flask server's URL

    headers = {'Content-Type': 'application/json'}
    payload = {'user_id': user_id}

    response = requests.post(f'{flask_server_url}/get_order', json=payload, headers=headers)

    orders = response.json().get('orders')

    context = {'orders': orders}

    return render(request, 'orders.html', context)