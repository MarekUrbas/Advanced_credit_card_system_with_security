from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///credit_card_system.db'
db = SQLAlchemy(app)


class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(16), unique=True, nullable=False)
    card_holder = db.Column(db.String(100), nullable=False)
    expiration_date = db.Column(db.String(5), nullable=False)
    balance = db.Column(db.Float, default=0.0)

    def charge(self, amount):
        if self.balance >= amount > 0:
            self.balance -= amount
            return True
        return False

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False

    def to_dict(self):
        return {
            'card_number': self.card_number,
            'card_holder': self.card_holder,
            'expiration_date': self.expiration_date,
            'balance': self.balance
        }


def authenticate(username, password):
    # Example authentication logic, replace with your own
    return username == 'admin' and password == 'password'


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if authenticate(username, password):
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/credit-cards', methods=['POST'])
def create_credit_card():
    data = request.get_json()
    card_number = data.get('card_number')
    card_holder = data.get('card_holder')
    expiration_date = data.get('expiration_date')

    existing_card = CreditCard.query.filter_by(card_number=card_number).first()
    if existing_card:
        return jsonify({'message': 'Card number already exists'}), 409

    new_card = CreditCard(
        card_number=card_number,
        card_holder=card_holder,
        expiration_date=expiration_date
    )
    db.session.add(new_card)
    db.session.commit()

    return jsonify({'message': 'Card created successfully'}), 201


@app.route('/credit-cards/<card_number>/charge', methods=['POST'])
def charge_credit_card(card_number):
    data = request.get_json()
    amount = data.get('amount')

    card = CreditCard.query.filter_by(card_number=card_number).first()
    if not card:
        return jsonify({'message': 'Card not found'}), 404

    if card.charge(amount):
        db.session.commit()
        return jsonify({'message': 'Transaction successful'}), 200
    else:
        return jsonify({'message': 'Transaction failed. Insufficient balance'}), 400


@app.route('/credit-cards/<card_number>/deposit', methods=['POST'])
def deposit_credit_card(card_number):
    data = request.get_json()
    amount = data.get('amount')

    card = CreditCard.query.filter_by(card_number=card_number).first()
    if not card:
        return jsonify({'message': 'Card not found'}), 404

    if card.deposit(amount):
        db.session.commit()
        return jsonify({'message': 'Deposit successful'}), 200
    else:
        return jsonify({'message': 'Deposit failed. Invalid amount'}), 400


@app.route('/credit-cards/<card_number
