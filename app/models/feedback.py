from app import mongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
class Feedback:
    collection = mongo.db.feedback

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def update(cls, feedback_id, data):
        print("Updating feedback-feedback.py", feedback_id)
        return cls.collection.update_one({"_id": ObjectId(feedback_id)}, {"$set": data})
    
    @classmethod
    def get_by_appointment(cls, appointment_id):
        return cls.collection.find({"appointment_id": appointment_id})
    

    @classmethod
    def get_all_feedbacks(cls):
        return cls.collection.find({})
