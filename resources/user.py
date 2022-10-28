from flask_restful import Resource, reqparse
from models.user import UserModel
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required,
    get_jwt_identity,
    get_jwt
)

from blocklist import BLOCKLIST

_user_parser=reqparse.RequestParser()
_user_parser.add_argument('username', 
                        type=str, 
                        required=True, 
                        help="This field is required."
                        )

_user_parser.add_argument('password', 
                        type=str, 
                        required=True, 
                        help="This field is required."
                        )

class UserRegister(Resource):

    def post(self):
        data=_user_parser.parse_args()
        if UserModel.find_by_username(data['username']):
            return{"message" : "A user with that username already exists"}, 400

        
        user=UserModel(**data)
        user.upsert()

        return{"message": "User has been created successfully."}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user=UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User could not be found'}, 404
        return user.json()


    @classmethod
    def delete(cls, user_id):
        user=UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User could not  be found'}, 404
        user.delete_from_db()
        return {'message': 'User has been deleted.'}, 200
    

class UserLogin(Resource):

    @classmethod
    def post(cls):
        data=_user_parser.parse_args()
        user=UserModel.find_by_username(data['username'])
        if user and user.password == data['password']:
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token= create_refresh_token(user.id)
            return{
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
            
        return {'message': 'Invalid Credentials'}, 401


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti=get_jwt()['jti'] #jti is "JWT IT", a unique identifier for a JWT.
        BLOCKLIST.add(jti)
        return{'message': 'Successfully logged out.'}, 200

class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user=get_jwt_identity()
        new_token=create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
