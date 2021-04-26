import pymongo
from settings import DB_URI


class DAO:
    def __init__(self):
        self.client = pymongo.MongoClient(DB_URI)
        self.db = self.client.test
