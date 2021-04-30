from typing import List, Set, Dict

import pymongo
from pymongo.collection import Collection

from settings import DB_URI


class DAO:
    def __init__(self):
        self.client = pymongo.MongoClient(DB_URI)
        self.db = self.client['fake-news-set']
        self.news: Collection = self.db.news
        self.tweets: Collection = self.db.tweets
        self.retweets: Collection = self.db.retweets

    def query_news(self) -> List[Dict[str, str]]:
        return self.news.find({}, {
            '_id': 0,
            'news_id': 1,
            'classification': 1,
        })

    def query_users(self) -> Set[str]:
        tweet_users: List[str] = self.tweets.distinct('user.id_str')
        retweet_users: List[str] = self.retweets.distinct('user.id_str')

        return set().union(tweet_users, retweet_users)

    def query_user_news_relation(self):
        pass
