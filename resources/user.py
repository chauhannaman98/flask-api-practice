from ast import Pass
from email import message
from json import load
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required
    )
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
import requests
from dotenv import load_dotenv
from os import getenv

from db import db
from models import UserModel, BLocklistModel
from schema import UserSchema, PasswordUpdateSchema

blp = Blueprint("Users", "users", description="Operations on users")
load_dotenv()


def send_simple_message():
	return requests.post(
		f"https://api.mailgun.net/v3/{getenv("MAILGUN_DOMAIN_NAME")}/messages",
		auth=("api", getenv("MAILGUN_API_KEY")),
		data={"from": "Excited User <mailgun@YOUR_DOMAIN_NAME>",
			"to": ["bar@example.com", "YOU@YOUR_DOMAIN_NAME"],
			"subject": "Hello",
			"text": "Testing some Mailgun awesomeness!"})

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(400, message="Username already registered.")
        
        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"]),
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "Registration successful"}, 201
    

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
            ).first()
        
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            # Authenticated
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200
    
        abort(401, message="Invalid credentials.")


@blp.route("/update-password")
class UpdatePassword(MethodView):
    @jwt_required()
    @blp.arguments(PasswordUpdateSchema)
    def put(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
            ).first()
        if user and pbkdf2_sha256.verify(user_data["old_password"], user.password):
            user.password = pbkdf2_sha256.hash(user_data["new_password"])
            try:
                db.session.add(user)
                db.session.commit()
            except SQLAlchemyError:
                abort(
                    500,
                    message="Unexpected error occurred while updating password."
                )
            return {"message": "Password update was successful. Please login again for new bearer token"}, 201
        
        abort(401, message="Invalid credentials.")


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()['jti']
        JTI = BLocklistModel(jti=jti)
        try:
            db.session.add(JTI)
            db.session.commit()
        except SQLAlchemyError as e:
            return {
                "error": e, 
                "message": "An error occurred while blocking refresh token."
            }
        return {"access_token": new_token}, 200


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        JTI = BLocklistModel(jti=jti)
        try:
            db.session.add(JTI)
            db.session.commit()
        except SQLAlchemyError as e:
            return {
                "error": e, 
                "message": "An error occurred while logging out."
            }
        
        return {"message": "User logged out."}, 201


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        if UserModel.query.filter(UserModel.id == user_id).first():
            user = UserModel.query.get(user_id)
            db.session.delete(user)
            db.session.commit()
            return {"message": "User has been deleted."}, 200
        
        return {"message": "User ID doesn't exist."}, 404