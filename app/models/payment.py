from app import mongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
class Payment:
    collection = mongo.db.payments

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def get_by_appointment(cls, appointment_id):
        return cls.collection.find_one({"appointment": ObjectId(appointment_id)})

    @classmethod
    def get_all_payments_for_date(cls, date):
        return list(cls.collection.find({"date": date}))


    @classmethod
    def valid_payment_details(cls, card_number, expiry_date, cvv):
        return True
    
    @classmethod
    def get_all_payments(cls):
        return list(cls.collection.find({}))
    
    @classmethod
    def process_payment(cls, card_number, expiry_date, cvv):
        return True