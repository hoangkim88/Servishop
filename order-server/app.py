import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from urllib.parse import quote
app = Flask(__name__)

password = '@123456@'
encoded_password = quote(password, safe='')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:{encoded_password}@localhost/ws-order'

db = SQLAlchemy(app)
account_service_url = 'http://localhost:5001'
product_service_url = 'http://localhost:5002'
cart_service_url = 'http://localhost:5003'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_total = db.Column(db.Float, nullable=False)


@app.route('/create_order', methods=['POST'])
def create_order():
    user_id = request.json.get('user_id')
    username = request.json.get('username')

    # Get the user's cart from the cart service
    cart_response = requests.post(f'{cart_service_url}/get_cart', json={'username': username})
    cart_data = cart_response.json()
    cart_items = cart_data.get('cart')
 
    if not cart_items:
        return jsonify({'message': 'Cart is empty'})

    # Calculate the total amount for the order and create order items
    total_amount = 0.0
    order_items = []
    for item in cart_items:
        product_id = item['product_id']
        quantity = item['quantity']

        # Get the product details from the product service
        product_response = requests.get(f'{product_service_url}/products/{product_id}')
        product_data = product_response.json()

        product_price = product_data.get('price')
        order_total = product_price * quantity
        total_amount += order_total

        order_item = OrderItem(product_id=product_id, quantity=quantity, order_total=order_total)
        order_items.append(order_item)
        db.session.add(order_item)  # Add order item to the session

    # Create the order in the order service
    order = Order(user_id=user_id, total_amount=total_amount, items=order_items)
    db.session.add(order)
    db.session.commit()  # Commit the changes to the database

    # Clear the user's cart in the cart service
    requests.post(f'{cart_service_url}/clear_cart', json={'username': username})

    return jsonify({'message': 'Order created successfully'})


@app.route('/get_order', methods=['POST'])
def get_order():
    user_id = request.json.get('user_id')

    # Get the user's orders from the order service
    orders = Order.query.filter_by(user_id=user_id).all()

    order_list = []
    for order in orders:
        order_dict = {
            'id': order.id,
            'user_id': order.user_id,
            'total_amount': order.total_amount,
            'order_items': []
        }

        # Get the order items for each order from the product service
        for item in order.items:
            product_id = item.product_id

            # Get the product details from the product service
            product_response = requests.get(f'{product_service_url}/products/{product_id}')
            product_data = product_response.json()

            order_item = {
                'product_id': product_id,
                'product_name': product_data.get('name'),
                'quantity': item.quantity,
                'order_total': item.order_total
            }

            order_dict['order_items'].append(order_item)

        order_list.append(order_dict)

    return jsonify({'orders': order_list})

def get_all_orders():
    # Get all orders from the order service
    orders = Order.query.all()

    order_list = []
    for order in orders:
        order_dict = {
            'id': order.id,
            'user_id': order.user_id,
            'total_amount': order.total_amount,
            'order_items': []
        }

        # Get the order items for each order from the product service
        for item in order.items:
            product_id = item.product_id

            # Get the product details from the product service
            product_response = requests.get(f'{product_service_url}/products/{product_id}')
            product_data = product_response.json()

            order_item = {
                'product_id': product_id,
                'product_name': product_data.get('name'),
                'quantity': item.quantity,
                'order_total': item.order_total
            }

            order_dict['order_items'].append(order_item)

        order_list.append(order_dict)

    return order_list


@app.route('/get_all_orders', methods=['GET'])
def get_all_orders_endpoint():
    orders = get_all_orders()
    return jsonify({'orders': orders})

if __name__ == '__main__':
    app.run(port=5004)


