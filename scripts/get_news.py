from dao.dao import DAO
from scripts.utils import (
    get_files,
    get_dirs,
    get_news_content,
    get_tweets,
    get_retweets,
)

BASE_PATH = '../../../PFC/News/'

if __name__ == '__main__':

    dao = DAO()

    for sub_folder in ('fake', 'notFake'):
        base_path = BASE_PATH + sub_folder
        files = get_files(base_path)

        for folder in get_dirs(base_path):
            path = base_path + f'/{folder}'

            news_content = get_news_content(path, classification=sub_folder).to_mongo()
            tweets = [
                tweet.to_mongo() for tweet in get_tweets(path, news_content)
            ]
            retweets = [
                retweet.to_mongo() for retweet in get_retweets(path, news_content)
            ]

            dao.news.insert_one(news_content)
            if tweets:
                dao.tweets.insert_many(tweets)
                if retweets:
                    dao.retweets.insert_many(retweets)
