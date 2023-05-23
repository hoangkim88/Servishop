from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

from urllib.parse import quote
app = Flask(__name__)

password = '@123456@'
encoded_password = quote(password, safe='')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:{encoded_password}@localhost/ws-product'

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))

@app.route('/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    product_list = []
    for product in products:
        product_dict = {
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': product.price,
            'description': product.description,
            'image': product.image
        }
        product_list.append(product_dict)
    return jsonify(product_list)

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        product_dict = {
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': product.price,
            'description': product.description,
            'image': product.image
        }
        return jsonify(product_dict)
    return jsonify({'message': 'Product not found'}), 404

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    product = Product(
        name=data['name'],
        category=data['category'],
        price=data['price'],
        description=data['description'],
        image=data['image']
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully'})

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if product:
        data = request.get_json()
        product.name = data['name']
        product.category = data['category']
        product.price = data['price']
        product.description = data['description']
        product.image = data['image']
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'})
    return jsonify({'message': 'Product not found'}), 404

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})
    return jsonify({'message': 'Product not found'}), 404

if __name__ == '__main__':
    app.run(port=5002)
