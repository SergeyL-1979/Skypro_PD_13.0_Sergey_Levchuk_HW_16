#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Configuration
from pprint import pprint

app = Flask(__name__)
app.config.from_object(Configuration)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

with app.app_context():
    db.create_all()

with app.app_context():
    try:
        db.session.execute('DROP MATERIALIZED VIEW IF EXISTS search_view;')
        db.session.commit()
    except:
        pass
    db.session.remove()  # DO NOT DELETE THIS LINE. We need to close sessions before dropping tables.
    db.drop_all()


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    # user_order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    # user_offer_id = db.Column(db.Integer, db.ForeignKey("offer.id"))
    # order_id = db.relationship("Order")

    # offer_id = db.relationship("Offer")

    def __repr__(self):
        return f"User: {self.first_name}, {self.last_name}, " \
               f"{self.age}, {self.email}, {self.role}, {self.role}"


class Order(db.Model):
    __tablename__ = "order"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Text)
    end_date = db.Column(db.Text)
    address = db.Column(db.String(255))
    price = db.Column(db.Float)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # offers = db.relationship("Offer")

    def __repr__(self):
        return f"Order: {self.name}, {self.description}, {self.start_date}" \
               f"{self.end_date}, {self.address}, {self.price}" \
               f"{self.customer_id}, {self.executor_id}"


class Offer(db.Model):
    __tablename__ = "offer"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # user_offer = db.relationship("User")

    def __repr__(self):
        return f"Offer: {self.id}, {self.order_id}, {self.executor_id}"


@app.route('/users')
def get_all_users():
    user_list = User.query.all()
    user_res = []
    for user in user_list:
        user_res.append(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "age": user.age,
                "email": user.email,
                "role": user.role,
                "phone": user.phone,
            }
        )

    return json.dumps(user_res)


@app.route('/users/<int:sid>')
def get_user_id(sid):
    user = User.query.get(sid)

    return json.dumps(
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age,
            "email": user.email,
            "role": user.role,
            "phone": user.phone,
        }
    )


@app.route('/orders')
def get_all_orders():
    orders_list = Order.query.all()
    order_res = []
    for order in orders_list:
        order_res.append(
            {
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": order.customer_id,
                "executor_id": order.executor_id,
            }
        )

    return json.dumps(order_res, ensure_ascii=False)


@app.route('/orders/<int:sid>')
def get_order_id(sid):
    order = Order.query.get(sid)

    return json.dumps(
        {
            "id": order.id,
            "name": order.name,
            "description": order.description,
            "start_date": order.start_date,
            "end_date": order.end_date,
            "address": order.address,
            "price": order.price,
            "customer_id": order.customer_id,
            "executor_id": order.executor_id,
        }, ensure_ascii=False
    )


@app.route('/offers')
def get_all_offers():
    offer_list = Offer.query.all()
    offer_res = []
    for offer in offer_list:
        offer_res.append(
            {
                "id": offer.id,
                "order_id": offer.order_id,
                "executor_id": offer.executor_id,
            }
        )

    return json.dumps(offer_res)


@app.route('/offers/<int:sid>')
def get_offer_id(sid):
    offer = Offer.query.get(sid)

    return json.dumps(
        {
            "id": offer.id,
            "order_id": offer.order_id,
            "executor_id": offer.executor_id,
        }
    )


# with open("db_json/users.json", encoding='utf-8') as file:
#     users = json.load(file)
#
# with open("db_json/orders.json", encoding='utf-8') as file:
#     orders = json.load(file)
#
# with open("db_json/offers.json", encoding='utf-8') as file:
#     offers = json.load(file)
#
# with app.app_context():
#     # Пересоздаем базу
#     db.drop_all()
#     db.create_all()
#     # создаем экземпляры пользователей
#     users_1 = [User(**user_data) for user_data in users]
#     orders_1 = [Order(**order_data) for order_data in orders]
#     offers_1 = [Offer(**offer_data) for offer_data in offers]
#     # добавляем в сессию и коммитим
#     db.session.add_all(users_1)
#     db.session.add_all(orders_1)
#     db.session.add_all(offers_1)
#     db.session.commit()
#
#     pprint(db.session.query(User).all())
#     pprint(db.session.query(Order).all())
#     pprint(db.session.query(Offer).all())

# user_1 = User(id=1, first_name="User_1", email="foo_1@foo_1.com", )
# user_2 = User(id=2, first_name="User_2", email="foo_2@foo_2.com", )
# order_1 = Order(name='Order_1', description='Foot', address="NY", price=5.5, customer_id=user_1, executor_id=user_2)
# order_2 = Order(name='Order_2', description='FWt', address="LA", price=10.5, customer_id=user_2, executor_id=user_2)
#
# print(f'Order: {order_1.customer_id.first_name}, User: {user_1.first_name}, Address: {order_1.address}')
# print(f'Order: {order_2.executor_id.first_name}, Address: {order_2.address}')

# with app.app_context():
#     db.create_all()
#     user_1 = User(
#         first_name="Nate",
#         last_name="Albertoh",
#         age=30,
#         email="peleg36@mymail.com",
#         role="executor",
#         phone="6158921977"
#     )
#
#     user_2 = User(
#         first_name="Cardew",
#         last_name="Hughik",
#         age=28,
#         email="jolyon37@mymail.com",
#         role="executor",
#         phone="6787970230"
#     )
#     user_3 = User(
#         first_name="Sandra",
#         last_name="Hughik",
#         age=45,
#         email="SANDRA@mymail.com",
#         role="customer",
#         phone="741852963357"
#     )
#     users_list = (user_1, user_2, user_3)
#     with db.session.begin():
#         # db.create_all()
#         # db.session.add(user_1)
#         # db.session.add(user_2)
#         # db.session.add(user_3)
#         db.session.add_all(users_list)
#         db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
