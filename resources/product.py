import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.product import ProductModel


class Product(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument('price', 
    type=float, 
    required=True, 
    help="This field is required!"
    )

    parser.add_argument('store_id', 
    type=int, 
    required=True, 
    help="Store id required"
    )



    @jwt_required()
    def get (self, name):
        item=ProductModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Product could not be found unfortunately'}, 404


    
    @jwt_required(fresh=True)
    def post(self, name):
        
        if ProductModel.find_by_name(name):
            return {"message" : "Product with name '{}' already exists.".format(name)}, 400
        
        data=Product.parser.parse_args()

        product = ProductModel(name, **data)

        try:
            product.upsert()
        except:
            return{'message': "Sorry, an error occured."}, 500

        return product.json(), 201
    

    @jwt_required()
    def delete(self, name):
        claims=get_jwt()
        if not claims['is_admin']:
            return{'message': 'Admin privilege required'}
        product=ProductModel.find_by_name(name)
        if product:
            product.delete_from_db()
            
        return {'message': 'Item deleted'}
        

    def put(self, name):
        data=Product.parser.parse_args()


        product=ProductModel.find_by_name(name)
        updated_product=ProductModel(name, **data)


        if product is None:
           product=ProductModel(name, **data)
        else:
            product.price=data['price']
        
        
        product.upsert()
        return product.json()


class ProductList(Resource):
    @jwt_required(optional=True)
    def get(self):
        user_id=get_jwt_identity()
        products = [product.json() for product in ProductModel.find_all()]
        if user_id:
            return {'products': products}, 200
        return{
            'products':[product['name'] for product in products], 
            'message': 'More data will be available if you log in'
        }, 200