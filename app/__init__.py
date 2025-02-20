from flask import Flask
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/appointment_management"
# app.config['JWT_SECRET_KEY'] = 'anil'  # Change this!
# jwt = JWTManager(app)

app.secret_key = 'adb'
mongo = PyMongo(app)

# def initialize_routes():
#     from app.routes import auth_routes, profile_routes
