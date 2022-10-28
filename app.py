import os
from pprint import pprint
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required

from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.product import Product, ProductList
from resources.store import Store, StoreList
from blocklist import BLOCKLIST
from db import db

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['PROPAGATE_EXCEPTIONS']=True

app.secret_key='SecretKey&'
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

jwt=JWTManager(app)

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity==1:
        return{'is_admin': True}
    return{'is_admin':False}

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti=jwt_payload['jti']
    return jti in BLOCKLIST

@jwt.expired_token_loader
def expired_token_callback(header, payload):
    return jsonify({
        'description': 'The token has expired, soorry.', 
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description': 'Signiture verification failed. Soorry', 
        'error': 'invalid_token'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        'description': 'The token is no fresh.', 
        'error': 'fresh_token_required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description': 'The token has been revoked.', 
        'error': 'token_revoked'
    }), 401

api.add_resource(Store, '/store/<string:name>')
api.add_resource(Product, '/product/<string:name>')
api.add_resource(ProductList, '/products')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')


db.init_app(app)

# pprint(app.config)


if __name__ == '__main__':
    app.run(debug=True, port=5000)