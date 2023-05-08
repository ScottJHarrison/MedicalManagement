import csv
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["medical_management"]
collection = db["patients"]

# Read CSV file and insert data into MongoDB
with open('C:\\Users\\Scott Harrison\\PycharmProjects\\pythonProject3\\static\\patients.csv', newline='', encoding='utf-8') as csvfile:

    reader = csv.DictReader(csvfile)
    data = [row for row in reader]

collection.insert_many(data)

print(f"Inserted {len(data)} records into the MongoDB collection")
