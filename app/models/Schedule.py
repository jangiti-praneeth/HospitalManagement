from app import mongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class Schedule:
    collection = mongo.db.schedule

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def get_by_doctor_id(cls, doctor_id):
        return list(cls.collection.find({"doctor_id": ObjectId(doctor_id)}))

    @classmethod
    def update(cls, doctor_id, data):
        return cls.collection.update_one({"doctor_id": ObjectId(doctor_id)}, {"$set": data})
