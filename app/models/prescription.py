from app import mongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
class Prescription:
    collection = mongo.db.prescriptions

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def get_by_appointment(cls, appointment_id):
        print("line 13", appointment_id)
        return cls.collection.find_one({"appointment": ObjectId(appointment_id)})

    @classmethod
    def update(cls, prescription_id, data):
        return cls.collection.update_one({"_id": ObjectId(prescription_id)}, {"$set": data})
    

    @classmethod
    def get_by_id(cls, prescription_id):
        return cls.collection.find_one({"_id": ObjectId(prescription_id)})
