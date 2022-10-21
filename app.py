from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from authentication import authenticate, identity
from user import UserRegister
from product import Product, ProductList

app = Flask (__name__)
app.secret_key='unilabSecretKey4%'
api = Api(app)

jwt=JWT(app, authenticate, identity)


api.add_resource(Product, '/product/<string:name>')
api.add_resource(ProductList, '/products')
api.add_resource(UserRegister, '/register')

if __name__ == '__main__':
    app.run(port=5000, debug=True)