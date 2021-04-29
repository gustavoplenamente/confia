import pymongo

from settings import DB_URI


class DAO:
    def __init__(self):
        self.client = pymongo.MongoClient(DB_URI)
        self.db = self.client['fake-news-set']
        self.news = self.db.news
        self.tweets = self.db.tweets
        self.retweets = self.db.retweets
