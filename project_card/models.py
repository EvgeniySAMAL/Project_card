from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Card(db.Model):
    '''модель карт'''
    id = db.Column(db.Integer, primary_key=True)
    serial_card = db.Column(db.String(2), nullable=False)                             #серия карт
    number_card = db.Column(db.Integer, nullable=False)                               #номер карт
    discount = db.Column(db.Integer, default=1)                                       #скидка по карте
    date_start_action = db.Column(db.DateTime, default=datetime.utcnow())             #дата и время активации карты
    date_finish_action = db.Column(db.DateTime, default=datetime.utcnow())            #дата и время деактивации карты
    date_last_use = db.Column(db.DateTime, default=datetime.utcnow())                 #дата и время последнего использования карты
    card_status = db.Column(db.Boolean, default=False)                                #статус карты (активна/неактивна)
    purchases = db.relationship('Purchase', backref='card', lazy='dynamic', cascade="all, delete-orphan")  #связь с моделью Purchase
    deleted = db.Column(db.Boolean, default=False)                                    #статус карты (удалена/нет)

    def __repr__(self):
        return '<Card %r>' % self.id


class Purchase(db.Model):
    ''' модель заказов '''
    id = db.Column(db.Integer, primary_key=True)
    date_of_purchase = db.Column(db.DateTime, default=datetime.utcnow())               #дата и время заказа
    discount_now = db.Column(db.Integer, default=0)                                    #скидка
    product = db.relationship('Product', backref='purchase', lazy='dynamic' ,cascade="all, delete-orphan")#связь с моделью Product
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'),nullable=False)           #связь с моделью Card

    def __repr__(self):
        return f'Заказ №{self.id}'


class Product(db.Model):
    ''' модель товаров '''
    id = db.Column(db.Integer, primary_key=True)
    name_product = db.Column(db.String(20), nullable=False)                            #наименование продукта/-ов
    product_cost = db.Column(db.Float, nullable=False)                                 #стоимость продукта/-ов
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'),nullable=False)   #связь с моделью Purchase



