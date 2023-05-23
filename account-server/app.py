from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flaskext.mysql import MySQL


from urllib.parse import quote
app = Flask(__name__)

password = '@123456@'
encoded_password = quote(password, safe='')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:{encoded_password}@localhost/ws-account'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __init__(self, username, password, role):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role


@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('role')

    # Check if the username is already taken
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    new_user = User(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()

    response = {
        'message': 'Registration successful',
        'user_id': new_user.id,
        'username': new_user.username,
        'role': new_user.role
    }

    return jsonify(response), 201


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.query.filter_by(username=username).first()
    print(user)
    if user and bcrypt.check_password_hash(user.password, password):
        response = {
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        }
        return jsonify(response), 200

    return jsonify({'message': 'Invalid username or password'}), 401

if __name__ == '__main__':
    app.run(port=5001)
