from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId, errors
# app/models/doctor.py

class Doctor:
    collection = mongo.db.doctors

    @classmethod
    def create(cls, data):  
        return cls.collection.insert_one(data)

    @classmethod
    def get_all_doctors(cls):
        return cls.collection.find()

    @classmethod
    def check_password(cls, doctor, password):  
        return check_password_hash(doctor["password"], password)

    @classmethod
    def get_by_email(cls, email):
        return cls.collection.find_one({"contactInfo.email": email})
    @classmethod
    def get_doctor_name_by_id(cls, doctor_id):
        try:
            # print(f"Querying for doctor_id: {doctor_id}")
            doctor = cls.collection.find_one({"_id": ObjectId(doctor_id)}) 
            return doctor['name'] if doctor else None
        except errors.PyMongoError as e:
            print(f"An error occurred while fetching the doctor's name: {e}")
            return None

    @classmethod
    def exists_by_email(cls, email):
        return cls.collection.find_one({"contactInfo.email": email}) is not None

    @classmethod
    def get_doctor_by_id(cls, doctor_id):
        try:
            # print(f"Querying for doctor_id: {doctor_id}")
            return cls.collection.find_one({"_id": ObjectId(doctor_id)}) 
        except errors.PyMongoError as e:
            print(f"An error occurred while fetching the doctor: {e}")
            return None