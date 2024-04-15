#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()
    bakery_serialized = bakery.to_dict()
    return make_response ( bakery_serialized, 200  )

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )

#Post Request
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():

    #Access form data
    name = request.form.get('name')
    price = request.form.get('price')
    bakery_id = request.form.get('bakery_id')

    #Create a new bakedGood object, creating a new instance 
    new_baked_good = BakedGood(name=name, price=price, bakery_id=bakery_id)

    #Add the new baked good instance into the database session
    db.session.add(new_baked_good)
    #command that actually executes those changes and saves them permanently to the database. Once you call commit(), the changes are applied to the database, and they become visible to other parts of your application and to external processes.
    db.session.commit() 

     # Return the data of the newly created baked good as a dictionary
    return new_baked_good.to_dict(), 201  # 201 status code indicates successful creation

#Patch Req
@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def patch_bakery(id):
    #first see the id matches with what we want to update
    bakery = Bakery.query.filter_by(id=id).first()

    #next do a GET req to see if the object exists bring it back
    if request.method == 'GET':
        bakery_serialized = bakery.to_dict()
        return make_response(bakery_serialized, 200)

    #Finally we will do an elif with the method Patch
    #set the attribute in a form , and then commit it 
    elif request.method == 'PATCH':
        for attr in request.form:
            setattr(bakery, attr, request.form.get(attr))

        db.session.add(bakery)
        db.session.commit()

        return bakery.to_dict(), 200

#Delete method

@app.route('/baked_goods/<int:id>', methods=['GET', 'DELETE'])
def baked_goods_by_id(id):
    #query the id with filter and match the id
    baked_good = BakedGood.query.filter(BakedGood.id == id).first()
        #condition with Get req first, and convert with .to_dict()
    if request.method == 'GET':
        return baked_good.to_dict(), 200
        #next condition with elif DELETE followed by deleting the baked_good
    elif request.method == 'DELETE':
        db.session.delete(baked_good)
        db.session.commit()
    
        return {"message": "record successfully deleted"}, 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)