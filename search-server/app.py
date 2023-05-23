import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
product_service_url = 'http://localhost:5002'

@app.route('/search_by_name', methods=['GET'])
def search_by_name():
    product_name = request.args.get('name')

    # Send a request to the product service to retrieve all products
    response = requests.get(f'{product_service_url}/products')

    if response.status_code == 200:
        products = response.json()
        # Filter products by name
        filtered_products = [p for p in products if product_name.lower() in p['name'].lower()]
        return jsonify(filtered_products)
    else:
        return jsonify({'message': 'Error searching by product name'}), response.status_code

@app.route('/search_by_category', methods=['GET'])
def search_by_category():
    category = request.args.get('category')

    # Send a request to the product service to retrieve all products
    response = requests.get(f'{product_service_url}/products')

    if response.status_code == 200:
        products = response.json()
        # Filter products by category
        filtered_products = [p for p in products if category.lower() == p['category'].lower()]
        return jsonify(filtered_products)
    else:
        return jsonify({'message': 'Error searching by category'}), response.status_code

@app.route('/filter_by_price', methods=['GET'])
def filter_by_price():
    sort_order = request.args.get('sort_order')

    # Send a request to the product service to retrieve all products
    response = requests.get(f'{product_service_url}/products')

    if response.status_code == 200:
        products = response.json()
        # Sort products by price
        filtered_products = sorted(products, key=lambda p: p['price'], reverse=(sort_order == 'high_to_low'))
        return jsonify(filtered_products)
    else:
        return jsonify({'message': 'Error filtering by price'}), response.status_code
    
@app.route('/categories', methods=['GET'])
def get_all_categories():
    # Send a request to the product service to retrieve all products
    response = requests.get(f'{product_service_url}/products')

    if response.status_code == 200:
        products = response.json()
        # Extract unique categories from products
        categories = list(set(p['category'] for p in products))
        return jsonify(categories)
    else:
        return jsonify({'message': 'Error retrieving categories'}), response.status_code


if __name__ == '__main__':
    app.run(port=5005)
