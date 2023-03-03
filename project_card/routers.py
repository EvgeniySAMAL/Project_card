import random

from flask import Flask, request, render_template, redirect
from project_card.models import Card, db, Purchase, Product
from datetime import datetime


def create_app():
    '''создание базы данных data_Card.db'''
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_Card.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

app = create_app()


@app.get('/')
def home():
    ''' главная страница, отодражаются все созданные и не удаленные карты'''
    f_parametrs = request.args.get('f_parametrs')
    if f_parametrs:                                             #отображение карт по выбранным полям (серия, номер) карты
        card_list = Card.query.filter(Card.serial_card.contains(f_parametrs) | Card.number_card.contains(f_parametrs)).all()
    else:
        card_list = Card.query.filter_by(deleted=False).all()   #отображение карт не помещенных в корзину
    return render_template('project_card/cards.html', cards=card_list, title='Главная страница')


@app.route('/trash', methods=['GET', 'POST'])
def trash():
    ''' страница корзины для удаленных карт'''
    if request.method == 'POST':

        if request.form.get('id_refresh'):                         #восстановление помещенной в корзину карты
            card = Card.query.get(request.form.get('id_refresh'))
            card.deleted = False
            db.session.commit()
            return redirect('/')
        elif request.form.get('delete_id'):                        #удаление помещенной в корзину карты
            card = Card.query.get(request.form.get('delete_id'))
            db.session.delete(card)
            db.session.commit()
            return redirect('/trash')

    elif request.method == 'GET':
        card_list = Card.query.filter_by(deleted=True).all()      #отображение всех помещенных в корзину карт на странице
        return render_template('project_card/trash_cards.html', cards=card_list, title='Главная страница')


@app.route('/card/<int:id>', methods=['GET', 'POST'])
def card_info(id):
    ''' детальная информация выбранной карты'''
    if request.method == 'GET':
        card = Card.query.get(id)                                                       #отображение выбранной карты
        purchases = db.session.query(Purchase).filter(Purchase.card_id == id).all()     #отображение заказов связанных с выбранной картой
        products_list = []
        prices = dict()
        for purchase in purchases:
            products = db.session.query(Product).filter(Product.purchase_id == purchase.id).all()  #отображение продуктов связанных с выбранной картой
            for p in products:
                products_list.append(p)
        for purchase in purchases:
            prices[purchase.id] = 0
            for p in products_list:
                if p.purchase_id == purchase.id:
                    prices[purchase.id] += p.product_cost

        return render_template('project_card/detail_card.html', card=card, purchases=purchases,
                               products_list=products_list, prices=prices, title='Информация')

    elif request.method == 'POST':
        try:
            card = Card.query.get(id)
            if request.form.get('delete'):                            #перемещение выбранной карты в корзину
                card.deleted = True                                   #путем изменения статус карты (удалена/нет)
                db.session.commit()
                return render_template('project_card/detail_card.html', title='Информация')

            elif request.form.get('status'):                          #изменение статуса выбранной карты
                if card.card_status:                                  #на (активна/неактивна)
                    card.card_status= False
                else:
                    card.card_status = True

            db.session.commit()
            return redirect(f'/card/{card.id}')

        except:
            return render_template('project_card/detail_card.html', title='Информация')


@app.route('/add', methods=['POST', 'GET'])
def add():
    ''' добавление новой карты'''
    if request.method == 'POST':
        serial_card = request.form.get('serial_card')
        number_card = request.form.get('number_card')
        discount_card = request.form.get('discount_card')
        new_cards = Card(
            serial_card=serial_card,                            #серия карты
            number_card=number_card,                            #номер карты
            discount=int(discount_card),                        #скидка по карте
            card_status=True,                                   #статус карты (по умолчанию активный)
            deleted=False                                       #статус карты (по умолчанию не перемещена в корзину)
        )
        try:
            db.session.add(new_cards)
            db.session.commit()
            return redirect('/')
        except:
            return 'При добавлении карты произошла ошибка'
    else:
        return render_template('project_card/create_card.html', title='Добавление')


@app.route('/generator', methods=['POST', 'GET'])
def generator():
    '''генератор карт, с указанием серии и количества генерируемых карт'''
    if request.method == 'POST':
        serial_card = request.form.get('serial_card')
        amount_card = int(request.form.get('amount_card'))  #генерируемых карт
        discount_card = request.form.get('discount_card')
        for i in range(amount_card):
            new_cards = Card(
                serial_card=serial_card,                    #серия карт
                number_card=random.randint(10000, 99999),   #рандомный номер карты
                discount=int(discount_card),                #скидка по картам
                card_status=True,                           #статус карты (по умолчанию активный)
                deleted=False                               #статус карты (по умолчанию не перемещена в корзину)
            )
            try:
                db.session.add(new_cards)
            except:
                return 'При добавлении карты произошла ошибка'
        db.session.commit()
        return render_template('project_card/generator.html', title='Добавление',info=amount_card)

    else:
        return render_template('project_card/generator.html', title='Добавление')



@app.route('/add_purchase', methods=['POST', 'GET'])
def add_purchase():
    '''добавление заказа в существующую карту '''
    if request.method == 'POST':
        card_id = request.form.get('card_id')
        card_discount = db.session.query(Card).get(card_id).discount
        db.session.query(Card).filter_by(id=card_id).update({Card.date_last_use: datetime.utcnow()})
        new_purchase = Purchase(
            card_id=card_id,                             #выбираем в какую карту добавить заказ
            discount_now=int(card_discount)              #скидка по карте определяется в соответствии с выбранной картой
        )
        try:
            db.session.add(new_purchase)
            db.session.commit()
            return redirect('/')
        except:
            return 'При добавлении заказа произошла ошибка'
    else:
        cards = Card.query.all()
        return render_template('project_card/add_purchase.html', title='Добавление', cards=cards)



@app.route('/add_product', methods=['POST', 'GET'])
def add_product():
    '''добавление продуктов в заказ'''
    if request.method == 'POST':
        name_product = request.form.get('name_product')
        product_cost = request.form.get('product_cost')
        purchase_id = request.form.get('purchase_id')
        new_product = Product(
            name_product=name_product,                         #наименование продукта
            product_cost=int(product_cost),                    #стоимость продукта
            purchase_id=purchase_id                            #выбор заказа для добавления в него продуктов
        )
        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect('/')
        except:
            return 'При добавлении продукта произошла ошибка'
    else:
        purchases = Purchase.query.all()
        return render_template('project_card/add_product.html', title='Добавление', purchases=purchases)
