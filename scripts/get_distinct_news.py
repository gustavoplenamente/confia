from dao.dao import DAO

if __name__ == '__main__':
    dao = DAO()
    news = dao.query_news()
    users = dao.query_users()
    user_news = dao.query_user_news_relation()

    print(news)
    print(users)
    print(user_news)
