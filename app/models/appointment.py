from app import mongo
from bson.objectid import ObjectId
from pymongo import MongoClient, errors
from app.models.doctor import Doctor
from app.models.patient import Patient
from datetime import datetime, timedelta



class Appointment:
    collection = mongo.db.appointments


    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def get_by_id(cls, appointment_id):
        return cls.collection.find_one({"_id": ObjectId(appointment_id)})

    @classmethod
    def get_by_doctor_date_time(cls, doctor, date, time):
        return cls.collection.find_one({"doctor": ObjectId(doctor), "date": date, "time": time})

    @classmethod
    def get_daily_appointments(cls, doctor, date):
        return list(cls.collection.find({"doctor": ObjectId(doctor), "date": date}))

    @classmethod
    def update(cls, appointment_id, data):
        return cls.collection.update_one({"_id": ObjectId(appointment_id)}, {"$set": data})

    @classmethod
    def cancel(cls, appointment_id):
        return cls.collection.update_one({"_id": ObjectId(appointment_id)}, {"$set": {"status": "cancelled"}})
    
    @classmethod
    def get_appointments_by_doctor(cls, doctor_id):
        try:
            # print(f"Querying for doctor_id: {doctor_id}")
            appointments = list(cls.collection.find({"doctor_id": doctor_id}))
            
            # Fetch each patient's name for the appointment and add it to the dictionary
            for appointment in appointments:
                patient_name = Patient.get_patient_name_by_id(appointment['patient_id'])
                appointment['patient_name'] = patient_name if patient_name else 'Unknown'

            return appointments
        except errors.PyMongoError as e:
            print(f"An error occurred: {e}")
            return []


    @classmethod
    def get_by_doctor_date_time(cls, doctor, date, time):
        print(f"Querying for doctor_id: {doctor}, date: {date}, time: {time}")
        return cls.collection.find_one({
            "doctor_id": doctor,
            "date": date,
            "time_slot": time
        })


    @classmethod
    def set_status(cls, appointment_id, status):
        return cls.collection.update_one({"_id": ObjectId(appointment_id)}, {"$set": {"status": status}})

    @classmethod
    def get_appointments_by_user(cls, user_id):
        try:
            # print(f"Querying for user_id: {user_id}")
            object_user_id = user_id
            appointments = list(cls.collection.find({"patient_id": object_user_id}))   
            for appointment in appointments:
                doctor_name = Doctor.get_doctor_name_by_id(appointment['doctor_id'])
                appointment['doctor_name'] = doctor_name if doctor_name else 'Unknown'
            return appointments
        except errors.PyMongoError as e:
            print(f"An error occurred: {e}")
            return []



# geenrate delete_appointment
    @classmethod
    def delete(cls, appointment_id):
        try:
            # print(f"Querying for appointment_id: {appointment_id}") 
            object_appointment_id = appointment_id
            cls.collection.delete_one({"_id": ObjectId(object_appointment_id)}) 
            print(f"Deleted appointment: {appointment_id}")
            return True
        except errors.PyMongoError as e:
            print(f"An error occurred: {e}")
            return False
        
#  add for update appointment
    @classmethod
    def update(cls, appointment_id, data):
        return cls.collection.update_one({"_id": ObjectId(appointment_id)}, {"$set": data})
    

    @classmethod
    def get_all_appointments(cls):
        return list(cls.collection.find({}))