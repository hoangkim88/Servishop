import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy


from urllib.parse import quote
app = Flask(__name__)

password = '@123456@'
encoded_password = quote(password, safe='')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:{encoded_password}@localhost/ws-cart'

db = SQLAlchemy(app)
account_service_url = 'http://localhost:5001'
product_service_url = 'http://localhost:5002'

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    


@app.route('/get_cart', methods=['POST'])
def get_cart():
    username = request.json.get('username')
    cart_items = CartItem.query.filter_by(username=username).all()

    cart = []
    for cart_item in cart_items:
        item = {
            'product_id': cart_item.product_id,
            'quantity': cart_item.quantity
        }
        cart.append(item)

    return jsonify({'cart': cart})



@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    username = request.json.get('username')
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity')

    # Check if the item already exists in the cart
    cart_item = CartItem.query.filter_by(username=username, product_id=product_id).first()

    if cart_item:
        # Item already exists, increment the quantity
        cart_item.quantity += quantity
    else:
        # Item does not exist, create a new cart item
        cart_item = CartItem(username=username, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()

    return jsonify({'message': 'Item added to cart successfully'})




@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    username = request.json.get('username')
    product_id = request.json.get('product_id')

    # Find the cart item
    cart_item = CartItem.query.filter_by(username=username, product_id=product_id).first()

    if cart_item:
        # Remove the cart item from the database
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from cart successfully'})

    return jsonify({'message': 'Item not found in cart'}), 404


@app.route('/update_cart', methods=['POST'])
def update_cart():
    username = request.json.get('username')
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity')

    # Find the cart item
    cart_item = CartItem.query.filter_by(username=username, product_id=product_id).first()

    if cart_item:
        # Update the quantity of the cart item
        cart_item.quantity = quantity
        db.session.commit()
        return jsonify({'message': 'Cart item updated successfully'})
    else:
        return jsonify({'message': 'Cart item not found'}), 404




@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    username = request.json.get('username')

    # Clear the cart items for the user
    CartItem.query.filter_by(username=username).delete()
    db.session.commit()

    return jsonify({'message': 'Cart cleared successfully'})



if __name__ == '__main__':
    app.run(port=5003)
