from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId, errors

class Patient:
    collection = mongo.db.patients

    @classmethod
    def create(cls, data):
        return cls.collection.insert_one(data)

    @classmethod
    def get_by_email(cls, email):
        return cls.collection.find_one({"contactInfo.email": email})

    @classmethod
    def check_password(cls, patient, password):
        return check_password_hash(patient["password"], password)

    @classmethod
    def exists_by_email(cls, email):
        return cls.collection.find_one({"contactInfo.email": email}) is not None

    @classmethod
    def get_patient_name_by_id(cls, patient_id):
        try:
            patient = cls.collection.find_one({"_id": ObjectId(patient_id)}) 
            # print(f"Found patient: {patient}")
            return patient['name'] if patient else None
        except errors.PyMongoError as e:
            print(f"An error occurred while fetching patient name: {e}")
            return None

    @classmethod
    def get_patient_by_id(cls, patient_id):
        try:
            patient = cls.collection.find_one({"_id": ObjectId(patient_id)}) 
            # print(f"Found patient: {patient}")
            return patient
        except errors.PyMongoError as e:
            print(f"An error occurred while fetching patient: {e}")
            return None
# get_by_appointment create this
    @classmethod
    def get_by_appointment(cls, appointment_id):
        # Your logic to fetch patient based on appointment_id
        appointment = mongo.db.appointments.find_one({"_id": ObjectId(appointment_id)})
        if appointment:
            return cls.collection.find_one({"_id": ObjectId(appointment['patient_id'])})
        return None
    
    @classmethod
    def get_all_patients(cls):
        return cls.collection.find({})


    @classmethod
    def get_patient_by_email(cls, email):
        print("line 59", email)
        patient_doc = cls.collection.find_one({"contactInfo.email": email})
        
        if patient_doc is not None:
            print("line 61", patient_doc.get("_id"))
            print(patient_doc)
            return patient_doc
        else:
            print("No patient found with email:", email)
            return None
