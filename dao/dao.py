from typing import List

import numpy as np
import pymongo
from pymongo.collection import Collection

from dao.aggregation_pipelines import (
    PROJECT_NEWS_ID_AND_USER_ID,
    PROJECT_USER_ID,
    union_with, GROUP_USER_ID, REPLACE_ROOT_FOR_NEWS_AND_USER,
)
from settings import DB_URI


class DAO:
    def __init__(self):
        self.client = pymongo.MongoClient(DB_URI)
        self.db = self.client['fake-news-set']
        self.news: Collection = self.db.news
        self.tweets: Collection = self.db.tweets
        self.retweets: Collection = self.db.retweets

    def query_news(self) -> np.ndarray:
        news_set = self.news.find({}, {
            '_id': 0,
            'news_id': 1,
            'classification': 1,
        })
        return np.array([
            [
                news['news_id'],
                news['classification']
            ]
            for news in news_set
        ])

    def query_users(self) -> np.ndarray:
        users = self.tweets.aggregate([
            PROJECT_USER_ID,
            union_with('retweets', [PROJECT_USER_ID]),
            GROUP_USER_ID
        ])
        return np.array([
            user['_id']
            for user in users
        ])

    def query_user_news_relation(self) -> np.ndarray:
        relations = self.tweets.aggregate([
            PROJECT_NEWS_ID_AND_USER_ID,
            union_with('retweets', [PROJECT_NEWS_ID_AND_USER_ID]),
            REPLACE_ROOT_FOR_NEWS_AND_USER
        ])
        return np.array([
            [
                relation['news_id'],
                relation['user_id']
            ]
            for relation in relations
        ])
