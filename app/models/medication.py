from app import mongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
class Medication:
    collection = mongo.db.medications

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def get_by_name(cls, name):
        return cls.collection.find_one({"name": name})

    @classmethod
    def get_by_prescription(cls, prescription_id):
        print("line 17", prescription_id)
        return list(cls.collection.find({"prescription": ObjectId(prescription_id)}))

    @classmethod
    def update(cls, prescription_id, data):
        return cls.collection.update_one({"_id": ObjectId(prescription_id)}, {"$set": data})
    
    @classmethod
    def get_all_medications(cls):
        return list(cls.collection.find({}))
