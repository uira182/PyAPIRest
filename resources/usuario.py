from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST

argumentos = reqparse.RequestParser()
argumentos.add_argument('login', type=str, required=True, help="The fild 'login' cannot be left clear")
argumentos.add_argument('senha', type=str, required=True, help="The fild 'senha' cannot be left clear")

class User(Resource):
    
    def get(self, user_id):
        
        hotel = UserModel.find_user(user_id)
        
        if hotel:
            return hotel.json()
        
        return {'message': 'User not found.'}, 404  # not found
    
    @jwt_required()
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        
        if user:
            
            try:
                user.delete_user()
            except:
                return {'message': 'an internal error ocurred trying to save user.'}, 500 # Internal server error
            
            return {'message': 'User deleted'}
        
        return {'message': 'User not found'}
    
class UserRegister(Resource):
    
    def post(self):
        dados = argumentos.parse_args()
        
        if UserModel.find_by_login(dados['login']):
            return{'message': "The login '{}' already exists.".format(dados['login'])}
        
        user = UserModel(**dados)
        user.save_user()
        return {'message': 'User created successfully!'}, 201 # Created
       
class UserLogin(Resource):
    
    @classmethod
    def post(cls):
        dados = argumentos.parse_args()
        
        user = UserModel.find_by_login(dados['login'])
        
        if user and safe_str_cmp(user.senha, dados['senha']):
            token_de_acesso = create_access_token(identity=user.user_id)
            return {'access_token': token_de_acesso}, 200 # Success
        
        return {'message': 'the username or password is incorrect.'}, 401 # Unauthorized
    
    
class UserLogout(Resource):
    
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti']
        BLACKLIST.add(jwt_id)
        return{'message': 'Logged out successfully!'}, 200 # Success