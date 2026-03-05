#!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        # Check if username is provided
        if not data.get('username'):
            return {'errors': ['Username must be present']}, 422
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return {'errors': ['Username already taken']}, 422
        
        try:
            # Create new user
            new_user = User(
                username=data['username'],
                image_url=data.get('image_url', ''),
                bio=data.get('bio', '')
            )
            new_user.password_hash = data['password']
            
            db.session.add(new_user)
            db.session.commit()
            
            # Store user_id in session
            session['user_id'] = new_user.id
            
            # Return user data
            return make_response(
                new_user.to_dict(only=('id', 'username', 'image_url', 'bio')),
                201
            )
            
        except ValueError as e:
            return {'errors': [str(e)]}, 422
        except Exception as e:
            return {'errors': ['An error occurred during signup']}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return make_response(
                    user.to_dict(only=('id', 'username', 'image_url', 'bio')),
                    200
                )
        
        return {'errors': ['Unauthorized']}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        
        # Find user by username
        user = User.query.filter_by(username=data.get('username')).first()
        
        # Authenticate user
        if user and user.authenticate(data.get('password')):
            session['user_id'] = user.id
            return make_response(
                user.to_dict(only=('id', 'username', 'image_url', 'bio')),
                200
            )
        
        return {'errors': ['Invalid username or password']}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id', None)
            return '', 204
        
        return {'errors': ['Unauthorized']}, 401

class RecipeIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return {'errors': ['Unauthorized']}, 401
        
        recipes = Recipe.query.all()
        recipes_data = []
        
        for recipe in recipes:
            recipe_dict = recipe.to_dict()
            recipe_dict['user'] = recipe.user.to_dict(only=('id', 'username', 'image_url', 'bio'))
            recipes_data.append(recipe_dict)
        
        return make_response(jsonify(recipes_data), 200)
    
    def post(self):
        if not session.get('user_id'):
            return {'errors': ['Unauthorized']}, 401
        
        data = request.get_json()
        
        try:
            # Validate required fields
            if not data.get('title'):
                return {'errors': ['Title must be present']}, 422
            
            if not data.get('instructions'):
                return {'errors': ['Instructions must be present']}, 422
            
            if len(data['instructions']) < 50:
                return {'errors': ['Instructions must be at least 50 characters long']}, 422
            
            new_recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data.get('minutes_to_complete'),
                user_id=session['user_id']
            )
            
            db.session.add(new_recipe)
            db.session.commit()
            
            # Get the recipe with nested user data
            recipe_dict = new_recipe.to_dict()
            recipe_dict['user'] = new_recipe.user.to_dict(only=('id', 'username', 'image_url', 'bio'))
            
            return make_response(jsonify(recipe_dict), 201)
            
        except ValueError as e:
            return {'errors': [str(e)]}, 422
        except Exception as e:
            return {'errors': ['An error occurred while creating the recipe']}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)