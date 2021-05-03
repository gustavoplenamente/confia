from typing import List


def union_with(collection: str, pipeline: List[dict]):
    return {
        '$unionWith': {
            'coll': collection,
            'pipeline': pipeline
        }
    }


PROJECT_USER_ID = {
    '$project': {
        'user.id_str': 1,
        '_id': 0
    }
}

PROJECT_NEWS_ID_AND_USER_ID = {
    '$project': {
        'news.news_id': 1,
        'user.id_str': 1,
        '_id': 0
    }
}

GROUP_USER_ID = {
    '$group': {
        '_id': "$user.id_str"
    }
}

REPLACE_ROOT_FOR_NEWS_AND_USER = {
    '$replaceRoot': {
        'newRoot': {
            'news_id': '$news.news_id',
            'user_id': '$user.id_str',
        }
    }
}
