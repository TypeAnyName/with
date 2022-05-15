import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from data import users, offers, orders
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(50))
    phone = db.Column(db.String(30))


class Orders(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text())
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(200))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Offers(db.Model):
    __tablename__ = "offers"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


def main():
    db.create_all()
    insert_data()
    app.run(debug=True)


def insert_data():
    new_users = []
    new_offers = []
    new_orders = []
    for user in users:
        new_users.append(
            User(
                id=user['id'],
                first_name=user["first_name"],
                last_name=user["last_name"],
                age=user['age'],
                email=user['email'],
                role=user['role'],
                phone=user['phone'],
            )
        )
    for order in orders:
        new_orders.append(
            Orders(
                name=order['name'],
                description=order['description'],
                start_date=datetime.strptime(order['start_date'], '%m/%d/%Y'),
                end_date=datetime.strptime(order['end_date'], '%m/%d/%Y'),
                address=order['address'],
                price=order['price'],
                customer_id=order['customer_id'],
                executor_id=order['executor_id'],
            )
        )
    for offer in offers:
        new_offers.append(
            Offers(
                id=offer['id'],
                order_id=offer['order_id'],
                executor_id=offer['executor_id'],
            )
        )
    with db.session.begin():
        db.session.add_all(new_users)
        db.session.add_all(new_offers)
        db.session.add_all(new_orders)


@app.route('/users', methods=['GET', 'POST'])
def users_():
    if request.method == 'GET':
        data = []
        for user_ in User.query.all():
            data.append({
                "id": user_.id,
                "first_name": user_.first_name,
                "last_name": user_.last_name,
                "age": user_.age,
                "email": user_.email,
                "role": user_.role,
                "phone": user_.phone,
            })
        return jsonify(data)
    elif request.method == 'POST':
        try:
            data = request.get_json()
            new_user = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                age=data['age'],
                email=data['email'],
                address=data['address'],
                role=data['role'],
                phone=data['phone'],
            )

            with db.session.begin():
                db.session.add(new_user)

            return 'Клиент добавлен'
        except TypeError:
            return "Проверьте вводимые данные"


@app.route('/users/<int:uid>', methods=['GET', "PUT", "DELETE"])
def users_by_id(uid):
    try:
        if request.method == 'GET':
            user = User.query.get(uid)
            data = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "age": user.age,
                "email": user.email,
                "role": user.role,
                "phone": user.phone,
            }
            return jsonify(data)
        elif request.method == 'PUT':
            data = request.get_json(uid)
            user = User.query.get(uid)
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.age = data['age']
            user.email = data['email']
            user.role = data['role']
            user.phone = data['phone']

            with db.session.begin():
                db.session.add(user)

            return "Данные пользователя обновлены"
        elif request.method == 'DELETE':
            user = User.query.get(uid)
            with db.session.begin():
                db.session.delete(user)
            return "Пользователь удалён"
    except AttributeError:
        return 'Пользователь с таким id  не найден'


@app.route('/orders', methods=['GET', 'POST'])
def orders_():
    if request.method == 'GET':
        data = []
        for order in Orders.query.all():
            customer = User.query.get(order.customer_id).first_name if User.query.get(
                order.customer_id) else order.customer_id
            executor = User.query.get(order.executor_id).first_name if User.query.get(
                order.executor_id) else order.executor_id
            data.append({
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": customer,
                "executor_id": executor,
            })
        return jsonify(data)
    elif request.method == 'POST':
        try:
            data = request.get_json()
            new_order = Orders(
                name=data['name'],
                description=data['description'],
                start_date=datetime.strptime(data['start_date'], '%m/%d/%Y'),
                end_date=datetime.strptime(data['end_date'], '%m/%d/%Y'),
                address=data['address'],
                price=data['price'],
                customer_id=data['customer_id'],
                executor_id=data['executor_id'],
            )

            with db.session.begin():
                db.session.add(new_order)
            return 'Заказ добавлен'
        except TypeError:
            return "Проверьте вводимые данные"


@app.route('/orders/<int:oid>', methods=['GET', "PUT", "DELETE"])
def orders_by_id(oid):
    try:
        if request.method == 'GET':
            order = Orders.query.get(oid)
            customer = User.query.get(order.customer_id).first_name if User.query.get(
                order.customer_id) else order.customer_id
            executor = User.query.get(order.executor_id).first_name if User.query.get(
                order.executor_id) else order.executor_id
            data = {
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": customer,
                "executor_id": executor,
            }
            return jsonify(data)
        elif request.method == 'PUT':
            data = request.get_json(oid)
            order = User.query.get(oid)
            order.name = data['name']
            order.description = data['description']
            order.start_date = datetime.strptime(data['start_date'], '%m/%d/%Y')
            order.end_date = datetime.strptime(data['end_date'], '%m/%d/%Y')
            order.address = data['address']
            order.price = data['price']
            order.customer_id = data['customer_id']
            order.executor_id = data['executor_id']

            with db.session.begin():
                db.session.add(order)
            return "Данные заказа обновлены"
        elif request.method == 'DELETE':
            order = Orders.query.get(oid)
            with db.session.begin():
                db.session.delete(order)
            return "Заказ удалён"
    except AttributeError:
        return 'Заказ с таким id  не найден'


@app.route('/offers', methods=['GET', 'POST'])
def offers_():
    if request.method == 'GET':
        data = []
        for offer in Offers.query.all():
            order_name = Orders.query.get(offer.order_id).name if Orders.query.get(
                offer.order_id) else offer.order_id
            executor = User.query.get(offer.executor_id).first_name if User.query.get(
                offer.executor_id) else offer.executor_id
            data.append({
                "id": offer.id,
                "order_id": offer.order_id,
                "order_name": order_name,
                "executor_id": executor,
            })
        return jsonify(data)
    elif request.method == 'POST':
        try:
            data = request.get_json()
            new_offer = Offers(
                id=data['id'],
                order_id=data['order_id'],
                executor_id=data['executor_id'],
            )

            with db.session.begin():
                db.session.add(new_offer)
            return "Данные добавлены"
        except TypeError:
            return "Проверьте вводимые данные"


@app.route('/offers/<int:ofid>', methods=['GET', "PUT", "DELETE"])
def offer_by_id(ofid):
    try:
        if request.method == 'GET':
            offer = Offers.query.get(ofid)
            order_name = Orders.query.get(offer.order_id).name if Orders.query.get(
                offer.order_id) else offer.order_id
            executor = User.query.get(offer.executor_id).first_name if User.query.get(
                offer.executor_id) else offer.executor_id
            data = {
                "id": offer.id,
                "order_id": offer.order_id,
                "order_name": order_name,
                "executor_id": executor,
            }
            return jsonify(data)
        elif request.method == 'PUT':
            data = request.get_json(ofid)
            offer = Offers.query.get(ofid)
            offer.id = data['id']
            offer.order_id = data['order_id']
            offer.executor_id = data['executor_id']

            with db.session.begin():
                db.session.add(offer)
            return "Данные обновлены"
        elif request.method == 'DELETE':
            offer = Offers.query.get(ofid)
            with db.session.begin():
                db.session.delete(offer)
            return "Данные удалёны"
    except AttributeError:
        return 'Данные с таким id  не найдены'


if __name__ == "__main__":
    main()

