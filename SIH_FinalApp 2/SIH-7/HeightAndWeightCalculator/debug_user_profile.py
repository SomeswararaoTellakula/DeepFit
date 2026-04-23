from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["sih2573"]

# Check user data
email = "afridpasha1983@gmail.com"
user = db.users.find_one({"email": email})
print(f"User data for {email}:")
print(user)

# Check measurements
collections = ['Height and Weight', 'Final_Estimated_Height_and_Weight', 'measurements']
for collection_name in collections:
    if collection_name in db.list_collection_names():
        measurement = db[collection_name].find_one(
            {"user_email": email}, 
            sort=[("timestamp", -1)]
        )
        print(f"\nLatest measurement in {collection_name}:")
        print(measurement)
    else:
        print(f"\nCollection {collection_name} does not exist")