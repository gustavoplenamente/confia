from dao.dao import DAO

if __name__ == '__main__':
    dao = DAO()
    news_ids = dao.query_news()
    print(news_ids)

    users = dao.query_users()
    print(users)
    print(len(users))
