import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.product import ProductModel


class Product(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument('price', 
    type=float, 
    required=True, 
    help="This field is required!"
    )


    @jwt_required()
    def get (self, name):
        item=ProductModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Product could not be found'}, 404



    def post(self, name):
        
        if ProductModel.find_by_name(name):
            return {"message" : "Product with name '{}' already exists.".format(name)}, 400
        
        data=Product.parser.parse_args()

        product = ProductModel(name, data['price'])

        try:
            product.upsert()
        except:
            return{'message': "Sorry, an error occured."}, 500

        return product.json(), 201
    

    @jwt_required()
    def delete(self, name):
        product=Product.find_by_name(name)
        if product:
            product.delete_from_db()
        
        return {'message': 'Item deleted'}
    

    def put(self, name):
        data=Product.parser.parse_args()


        product=ProductModel.find_by_name(name)
        updated_product=ProductModel(name, data['price'])


        if product is None:
           product=ProductModel(name, data['price'])
        else:
            product.price=data['price']
        
        product.save_to_db()

        return product.json()


class ProductList(Resource):
    def get(self):
        connection=sqlite3.connect('data.db')
        cursor=connection.cursor()

        query="SELECT * FROM products"
        result=cursor.execute(query)
        products=[]
        for row in result:
            products.append({'name':row[0], 'price': row[1]})

        connection.close()

        return{'products':products}