import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

class Product(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument('price', 
    type=float, 
    required=True, 
    help="This field is required!"
    )


    @jwt_required()
    def get (self, name):
        item=self.find_by_name(name)
        if item:
            return item
        return {'message': 'Product could not be found'}, 404
    
    @classmethod
    def find_by_name(cls, name):
        connection=sqlite3.connect('data.db')
        cursor=connection.cursor()
        query="SELECT * FROM products WHERE name=?"
        result=cursor.execute(query, (name,))
        row =result.fetchone()
        connection.close

        if row:
            return {"product": {'name':row[0], 'price':row[1]}}

    def post(self, name):
        
        if self.find_by_name(name):
            return {"message" : "Product with name '{}' already exists.".format(name)}, 400
        
        data=Product.parser.parse_args()

        product = {'name' : name, 'price' : data['price']}

        try:
            self.insert(product)
        except:
            return{'message': "Unexpected error occured."}, 500

        return product, 201
    
    @classmethod
    def insert(cls, product):
        connection=sqlite3.connect('data.db')
        cursor=connection.cursor()
        query="INSERT INTO products VALUES(?, ?)"
        cursor.execute(query, (product['name'], product['price']))

        connection.commit()
        connection.close()
    

    @jwt_required()
    def delete(self, name):
        connection=sqlite3.connect('data.db')
        cursor=connection.cursor()
        query="DELETE FROM products WHERE name=?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()
        
        return {'message' : 'Product has been deleted'}
    

    def put(self, name):
        data=Product.parser.parse_args()


        product=self.find_by_name(name)
        updated_product={'name': name, 'price': data['price']}


        if product is None:
            try:
                self.insert(updated_product)
            except:
                return {"message": "Unexpected Error Occured"}, 500
        else:
            try:
                self.update(updated_product)
            except:
                return {"message": "Unexpected Error Occured"}, 500
        return updated_product
    
    @classmethod
    def update(cls, product):
        connection=sqlite3.connect('data.db')
        cursor=connection.cursor()

        query="Update products SET price=? WHERE name=?"
        cursor.execute(query, (product['price'], product['name']))

        connection.commit()
        connection.close()



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