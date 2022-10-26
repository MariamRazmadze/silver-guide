from flask_restful import Resource, reqparse
from models.user import UserModel



class UserRegister(Resource):

    parser=reqparse.RequestParser()
    parser.add_argument('username', 
                        type=str, 
                        required=True, 
                        help="This field is required."
                        )

    parser.add_argument('password', 
                        type=str, 
                        required=True, 
                        help="This field is required."
                        )


    def post(self):

        data=UserRegister.parser.parse_args()
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