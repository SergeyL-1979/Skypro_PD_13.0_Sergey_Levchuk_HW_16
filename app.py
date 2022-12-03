#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime
from flask import Flask, render_template, redirect, request
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

# ====================== МОДЕЛИ БАЗЫ ДАННЫХ ================================
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

# ================ КОНЕЦ СОЗДАНИЯ МОДЕЛЕЙ БД ==============================

# ================ ВЬЮШКА И КОД ОБРАБОТКИ ЗАПРОСОВ К БД ===================
@app.route('/')
def add_user():
    return render_template("add_users.html")


def add_user_profile(user_name, user_surname, user_age, user_email, user_role, user_phone):
    """
    Создаем нового пользователя в БД
    """
    users_new = User(
        first_name=user_name,
        last_name=user_surname,
        age=user_age,
        email=user_email,
        role=user_role,
        phone=user_phone,
    )
    with app.app_context():
        # db.drop_all()
        # db.create_all()
        db.session.add(users_new)
        db.session.commit()


@app.route('/add-user', methods=["POST"])
def save_user():
    """
    ВВОДИМ ДАННЫЕ НА НОВОГО ПОЛЬЗОВАТЕЛЯ
    """
    first_name = request.form.get("user_name")
    last_name = request.form.get("user_surname")
    age = request.form.get("user_age")
    email = request.form.get("user_email")
    role = request.form.get("user_role")
    phone = request.form.get("user_phone")
    add_user_profile(
        first_name,
        last_name,
        age,
        email,
        role,
        phone,
    )
    return f"{first_name}, {last_name}, {age}, {email}, {role}, {phone}"


@app.route('/users')
def get_all_users():
    """
    ВЫВОДИМ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ
    """
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
    """
    ЗАПРОС ДАННЫХ ОДНОГО ПОЛЬЗОВАТЕЛЯ
    """
    user = User.query.filter_by(id=sid).first_or_404()
    # user = User.query.get(sid)
    return json.dumps(
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age,
            "email": user.email,
            "role": user.role,
            "phone": user.phone,
        }, ensure_ascii=False
    )


@app.route('/edit/<int:pk>', methods=['PUT'])
def get_user_update(pk):
    # user = get_user_id(pk)
    user = User.query.get(pk)

    user.first_name = request.form.get("first_name")
    user.last_name = request.form.get("last_name")
    user.age = request.form.get("age")
    user.email = request.form.get("email")
    user.role = request.form.get("role")
    user.phone = request.form.get("phone")
    db.session.commit()

    return f"User_edit: {user}"


@app.route('/delete/<int:pk>', methods=['POST'])
def get_user_delete(pk):
    user_del = User.query.get(pk)
    db.session.delete(user_del)
    db.session.commit()
    return f"USER DELETE: {user_del}"


@app.route('/orders')
def get_all_orders():
    """
    ЗАПРОС НА ВЫВОД ВСЕХ ДАННЫХ ОРДЕРОВ
    """
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
    """
    ЗАПРОС НА ВЫВОД КОНКРЕТНОГО ОРДЕРА ПО ЕГО ID
    """
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
    """
    ВСЕ ОФФЕРЫ
    """
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
    """
    ОФФЕР ПО ID
    """
    offer = Offer.query.get(sid)

    return json.dumps(
        {
            "id": offer.id,
            "order_id": offer.order_id,
            "executor_id": offer.executor_id,
        }
    )

# ====== ЧТЕНИЯ ДАННЫХ ИЗ JSON И ДОБАВЛЕНИЯ ИХ В БД ========================
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
# =============== КОНЕЦ ЧТЕНИЯ ДАННЫХ ИЗ ФАЙЛА =============================

# user_1 = User(id=1, first_name="User_1", email="foo_1@foo_1.com", )
# user_2 = User(id=2, first_name="User_2", email="foo_2@foo_2.com", )
# order_1 = Order(name='Order_1', description='Foot', address="NY", price=5.5, customer_id=user_1, executor_id=user_2)
# order_2 = Order(name='Order_2', description='FWt', address="LA", price=10.5, customer_id=user_2, executor_id=user_2)
#
# print(f'Order: {order_1.customer_id.first_name}, User: {user_1.first_name}, Address: {order_1.address}')
# print(f'Order: {order_2.executor_id.first_name}, Address: {order_2.address}')
# with app.app_context():
#     res_1 = db.session.query(User, Order).join(Order, User.id==Order.executor_id).all()
#     res_2 = db.session.query(User, Order).join(Order, User.id==Order.customer_id).all()
#     res_3 = db.session.query(Order, Offer).join(Order, Offer.id==Order.executor_id).all()
#     res_4 = db.session.query(Order, Offer).join(Offer, Order.id==Offer.order_id).all()
# pprint(res_1)
# pprint(res_2)
# pprint(res_3)
# pprint(res_4)
#     user_1 = User.query.get(18)
# pprint(user_1.first_name)
# pprint(user_1.last_name)
# pprint(user_1.age)
# pprint(user_1.role)
# pprint(user_1.phone)
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
