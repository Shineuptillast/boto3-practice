from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os


class mongodb_connection:
    def __init__(self):
        self.uri = os.getenv('MONGODB_URL').format(os.getenv('PASSWORD'))
        # Create a new client and connect to the server
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Connected to Mongodb")
        except Exception as e:
            print(e)

    def create_database(self, dbn):
        self.db = self.client[dbn]
        return self.db

    def create_collection(self, collection_name):
        return self.db[collection_name]

    def list_collection(self):
        return self.db.list_collection_names()

    def insert_one_record(self, collection, record):
        self.db[collection].insert_one(record)

    def drop_collection(self, collection):
        self.db.drop_collection(collection)

    def retreive(self, collection):
        result = []
        r = self.db[collection].find()
        for i in r:
            result.append(i)
        return result

    def latest_to_date(self, collection):
        result = self.db[collection].find().sort([('to_date', -1)]).limit(1)
        result = list(result)
        return result
