import json
import os
from typing import List

from entities.news import NewsContent
from entities.tweet import Tweet, Retweet


def get_dirs(path: str):
    return next(os.walk(path))[1]


def get_files(path: str):
    return next(os.walk(path))[2]


def get_file(path: str, file_name: str):
    return os.path.join(path, file_name)


def get_news_content(path: str, **kwargs) -> NewsContent:
    news_content_file = get_file(path, 'news content.json')
    with open(news_content_file) as news_content:
        data = json.load(news_content)
        data.update(kwargs)
        return NewsContent(**data)


def get_tweets(path: str, news: NewsContent) -> List[Tweet]:
    path += '/tweets'
    files = get_files(path)

    tweets = []
    for file_name in files:
        tweet_file = get_file(path, file_name)
        with open(tweet_file) as tweet:
            data = json.load(tweet)
            data['id_number'] = data.pop('id')
            data['news'] = news
            tweets.append(data)

    return [
        Tweet(**tweet)
        for tweet in tweets
    ]


def get_retweets(path: str, news: NewsContent) -> List[Retweet]:
    path += '/retweets'
    files = get_files(path)

    retweets = []
    for file_name in files:
        retweet_file = get_file(path, file_name)
        with open(retweet_file) as retweet:
            data = json.load(retweet)
            if retweets_data := data['retweets']:
                for rt in retweets_data:
                    rt['id_number'] = rt.pop('id')
                    rt['news'] = news
                    retweets.append(rt)

    return [
        Retweet(**retweet)
        for retweet in retweets
    ]
