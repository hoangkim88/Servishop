from django.shortcuts import render
import requests
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponseRedirect

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
            user_role = response.json().get('role')

            if user_role == 'admin':
                # Redirect the admin to the home page
                request.session['user_id'] = user_id
                request.session['username'] = username
                request.session['role'] = user_role
                return redirect('home')
        error_message = response.json().get('message')
        return render(request, 'login.html', {'error': error_message})

    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

def manage_product(request):
    # Check if the user is authenticated and has the required role
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('login')

    # Your logic for managing products goes here
    url = 'http://localhost:5002/products'  # Update with the Flask server URL
    response = requests.get(url)
    products = response.json()

    return render(request, 'manage_product.html', {'products': products})


def manage_order(request):
    # Check if the user is authenticated and has the required role
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('login')

    # Get all orders from the order service
    response = requests.get('http://localhost:5004/get_all_orders')
    orders = response.json().get('orders', [])

    return render(request, 'manage_order.html', {'orders': orders})

def add_product(request):
    # Check if the user is authenticated and has the required role
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('login')

    # Your logic for adding a new product goes here

    return render(request, 'add_product.html')

def save_product(request):
    if request.method == 'POST':
        url = 'http://localhost:5002/products'  # Update with the Flask server URL
        data = {
            'name': request.POST.get('name'),
            'category': request.POST.get('category'),
            'price': request.POST.get('price'),
            'description': request.POST.get('description'),
            'image': request.POST.get('image')
        }
        response = requests.post(url, json=data)

        if response.status_code == 200:  # Product added successfully
            return redirect('manage_product')

        error_message = response.json().get('message')
        return render(request, 'add_product.html', {'error': error_message})

    return render(request, 'add_product.html')

def update_product(request, product_id):
    # Check if the user is authenticated and has the required role
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('login')

    url = f'http://localhost:5002/products/{product_id}'  # Update with the Flask server URL

    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'category': request.POST.get('category'),
            'price': request.POST.get('price'),
            'description': request.POST.get('description'),
            'image': request.POST.get('image')
        }
        response = requests.put(url, json=data)

        if response.status_code == 200:  # Product updated successfully
            return redirect('manage_product')

        error_message = response.json().get('message')
        return render(request, 'update_product.html', {'error': error_message})

    # Retrieve the product details from the server
    response = requests.get(url)
    if response.status_code == 200:
        product = response.json()
        return render(request, 'update_product.html', {'product': product})

    return render(request, 'update_product.html', {'error': 'Product not found'})

def delete_product(request, product_id):
    # Check if the user is authenticated and has the required role
    if not request.session.get('user_id') or request.session.get('role') != 'admin':
        return redirect('login')

    # Your logic for deleting the product goes here
    url = f'http://localhost:5002/products/{product_id}'  # Update with the Flask server URL
    response = requests.delete(url)

    if response.status_code == 200:  # Product deleted successfully
        return redirect('manage_product')
    else:
        error_message = response.json().get('message')
        return render(request, 'manage_product.html', {'error_message': error_message})

