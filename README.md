# Skypro_PD_13.0_Sergey_Levchuk_HW_16

Выполнены ШАГИ с 1 по 8

НО не получилось реализовать ШАГ 7 связку пользователей с полями ORDER **customer_id** и
**executor_id**.
---
Есть вариант, не совсем рабочий
```python
@app.route('/orders/<int:sid>')
def get_order_id(sid):
    # == Есть решение отображения пользователей, но работает только с одним вхождением ==
    res_1 = db.session.query(Order, User).join(Order, User.id == Order.executor_id).first()
    res_2 = db.session.query(Order, User).join(Order, User.id == Order.customer_id).first()
    return f"{res_2}, {res_1}"
```
Как передать **sid** для вывода связанных с ордером пользователей не понимаю

Так же не вообще не удалось реализовать такое же совмещение ORDER с OFFER
Есть такой вариант
```python
with app.app_context():
    res_3 = db.session.query(Order, Offer).join(Order, Offer.id==Order.executor_id).all()
    res_4 = db.session.query(Order, Offer).join(Offer, Order.id==Offer.order_id).all()

print(res_3)
print(res_4)
```
Но снова работает выводя все результаты или только самый первый
В общем я с этим не разобрался, как и не смог разобраться с правильным запросом SQL для проверки связей между таблицами