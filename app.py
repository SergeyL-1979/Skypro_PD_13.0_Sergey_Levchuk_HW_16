#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# ===========================================================
from config import Configuration
# ===========================================================

app = Flask(__name__)
app.config.from_object(Configuration)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
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
        return f"User: {self.id}, {self.first_name}"


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow())
    end_date = db.Column(db.DateTime)
    address = db.Column(db.String(255))
    price = db.Column(db.Float)
    customer_id = db.Column(db.Integer, db.ForeignKey("offer.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    offers = db.relationship("Offer")

    def __repr__(self):
        return f"Order: {self.id}, {self.name}"


class Offer(db.Model):
    __tablename__ = "offer"

    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    order_id = db.Column(db.Integer)
    executor_id = db.Column(db.Integer)

    # user_offer = db.relationship("User")

    def __repr__(self):
        return f"Offer: {self.id}, {self.order_id}, {self.executor_id}"


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
