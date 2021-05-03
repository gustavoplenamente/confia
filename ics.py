from collections import Counter

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from sklearn.base import ClassifierMixin, BaseEstimator
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split

from dao.dao import DAO


class ICS(ClassifierMixin, BaseEstimator):

    def __init__(self, laplace_smoothing=0.01, omega=0.5):

        self.laplace_smoothing = laplace_smoothing
        self.omega = omega

        self.dao = DAO()
        self.news = self.dao.query_news()
        self.users = self.dao.query_users()
        self.news_users = self.dao.query_user_news_relation()

        self.X_train_news = None
        self.X_test_news = None
        self.train_news_users = None
        self.test_news_users = None
        self.fake_count = None
        self.not_fake_count = None

    def init_params(self, test_size: float):

        # Split news dataset into train and test
        labels = [news["classification"] for news in self.news]
        news_ids = [news["news_id"] for news in self.news]

        self.X_train_news, self.X_test_news, *_ = train_test_split(news_ids,
                                                                   labels,
                                                                   test_size=test_size,
                                                                   stratify=labels)

        # Armazena em self.train_news_users as notícias compartilhadas por cada usuário.
        self.train_news_users = (
            [news_id]
            for relation in news_ids
        )

        self.test_news_users = pd.merge(self.X_test_news, self.news_users,
                                        left_on="id_news", right_on="id_news")

        # Conta a quantidade de noticias verdadeiras e falsas presentes no conjunto
        counter = Counter(labels)

        self.fake_count = counter['fake']
        self.not_fake_count = counter['notFake']

        # Filtra apenas os usuários que não estão em ambos os conjuntos de treino e teste.
        self.train_news_users = self.train_news_users[
            self.train_news_users["id_social_media_account"].isin(
                self.test_news_users["id_social_media_account"])]

        # Inicializa os parâmetros dos usuários.
        totR = 0
        totF = 0
        alphaN = totR + self.laplace_smoothing
        umAlphaN = ((totF + self.laplace_smoothing) / (
            self.fake_count + self.laplace_smoothing)) * (
                       self.not_fake_count + self.laplace_smoothing)
        betaN = (umAlphaN * (totR + self.laplace_smoothing)) / (
            totF + self.laplace_smoothing)
        umBetaN = totF + self.laplace_smoothing
        probAlphaN = alphaN / (alphaN + umAlphaN)
        probUmAlphaN = 1 - probAlphaN
        probBetaN = betaN / (betaN + umBetaN)
        probUmBetaN = 1 - probBetaN
        self.users["probAlphaN"] = probAlphaN
        self.users["probUmAlphaN"] = probUmAlphaN
        self.users["probBetaN"] = probBetaN
        self.users["probUmBetaN"] = probUmBetaN

    def assess(self):
        """
        Assessment Phase: assess news based on each user parameters
        obtained on Training Phase
        """
        predicted_labels = []
        unique_id_news = self.test_news_users["id_news"].unique()

        for newsId in unique_id_news:
            # recupera os ids de usuário que compartilharam a notícia representada por 'newsId'.
            usersWhichSharedTheNews = list(
                self.news_users["id_social_media_account"].loc[
                    self.news_users["id_news"] == newsId])

            productAlphaN = 1.0
            productUmAlphaN = 1.0
            productBetaN = 1.0
            productUmBetaN = 1.0

            for userId in usersWhichSharedTheNews:
                i = self.users.loc[
                    self.users["id_social_media_account"] == userId].index[0]

                productAlphaN = productAlphaN * self.users.at[i, "probAlphaN"]
                productUmBetaN = productUmBetaN * self.users.at[i, "probUmBetaN"]

            # inferência bayesiana
            reputation_news_tn = (self.omega * productAlphaN * productUmAlphaN) * 100
            reputation_news_fn = ((
                                      1 - self.omega) * productBetaN * productUmBetaN) * 100

            if reputation_news_tn >= reputation_news_fn:
                predicted_labels.append(0)
            else:
                predicted_labels.append(1)

        # mostra os resultados da matriz de confusão e acurácia.
        print(confusion_matrix(self.X_test_news["ground_truth_label"],
                               predicted_labels))
        print(
            accuracy_score(self.X_test_news["ground_truth_label"], predicted_labels))

    def fit(self, X: ArrayLike, y: ArrayLike):
        """
        Training phase: evaluate users parameters based on Implicit Crowd Signals

        X: [news_id, user_id, classification]

        news_id: int
        user_id: int
        classification: int
        """
        NEWS_INDEX = 0
        USER_INDEX = 1
        LABEL_INDEX = 2
        PROB_ALPHA_INDEX = 3
        PROB_ALPHA_COMPLEMENT_INDEX = 4
        PROB_BETA_INDEX = 5
        PROB_BETA_COMPLEMENT_INDEX = 6

        self.news = X[:, NEWS_INDEX]
        self.users = X[:, USER_INDEX]
        self.labels = X[:, LABEL_INDEX]

        self.news_unique = np.unique(self.news)
        self.users_unique = np.unique(self.users)
        self.labels_unique, labels_count = np.unique(self.labels, return_count=True)

        if not {self.labels_unique}.issubset({0, 1}):
            raise ValueError('label should be in {0, 1}.')

        self.fake_count, self.not_fake_count = labels_count

        self.total = X.shape[0]
        self.total_users = len(self.users_unique)
        self.total_news = len(self.news_unique)

        i = 0
        for user_id in self.users_unique:
            i += 1
            progress = (i / self.total_users) * 100
            print(f'Progresso do fit: {progress:.2f}%', flush=True)

            is_user = self.users == user_id
            user_labels = X[is_user, LABEL_INDEX]

            _, labels_count = np.unique(user_labels, return_counts=True)

            total_not_fake, total_fake = labels_count

            alpha, alpha_complement, beta, beta_complement = \
                self._get_alpha_and_beta(total_fake, total_not_fake)

            prob_alpha, prob_alpha_complement = \
                self._get_probabilities(alpha, alpha_complement)

            prob_beta, prob_beta_complement = \
                self._get_probabilities(beta, beta_complement)

            self.users.

        # i = 0
        # self.init_params(test_size)
        # users_unique = self.train_news_users["id_social_media_account"].unique()
        # total = len(users_unique)
        #
        # for userId in users_unique:
        #     i = i + 1
        #     print("", end="Progresso do treinamento: {0:.2f}%\r".format(
        #         float((i / total) * 100)), flush=True)
        #
        #     # obtém os labels das notícias compartilhadas por cada usuário.
        #     newsSharedByUser = list(self.train_news_users["ground_truth_label"].loc[
        #                                 self.train_news_users[
        #                                     "id_social_media_account"] == userId])
        #
        #     # calcula a matriz de opinião para cada usuário.
        #     totR = newsSharedByUser.count(0)
        #
        #     totF = newsSharedByUser.count(1)
        #
        #     alphaN = totR + self.laplace_smoothing
        #
        #     umAlphaN = ((totF + self.laplace_smoothing) / (
        #         self.fake_count + self.laplace_smoothing)) * (
        #                    self.not_fake_count + self.laplace_smoothing)
        #
        #     betaN = (umAlphaN * (totR + self.laplace_smoothing)) / (
        #         totF + self.laplace_smoothing)
        #
        #     umBetaN = totF + self.laplace_smoothing
        #
        #     # calcula as probabilidades para cada usuário.
        #     probAlphaN = alphaN / (alphaN + umAlphaN)
        #     probUmAlphaN = 1 - probAlphaN
        #     probBetaN = betaN / (betaN + umBetaN)
        #     probUmBetaN = 1 - probBetaN
            self.users.loc[self.users[
                               "id_social_media_account"] == userId, "probAlphaN"] = probAlphaN
            self.users.loc[self.users[
                               "id_social_media_account"] == userId, "probBetaN"] = probBetaN
            self.users.loc[self.users[
                               "id_social_media_account"] == userId, "probUmAlphaN"] = probUmAlphaN
            self.users.loc[self.users[
                               "id_social_media_account"] == userId, "probUmBetaN"] = probUmBetaN

        self.assess()
        return self.users

    def _get_probabilities(self, x, x_complement):
        prob_alpha = x / (x + x_complement)
        return prob_alpha, 1 - prob_alpha

    def _get_alpha_and_beta(self, total_fake, total_not_fake):
        _total_fake = total_fake + self.laplace_smoothing
        _total_not_fake = total_not_fake + self.laplace_smoothing
        _fake_count = self.fake_count + self.laplace_smoothing
        _not_fake_count = self.not_fake_count + self.laplace_smoothing

        alpha = _total_not_fake
        alpha_complement = _total_fake / (_fake_count * _not_fake_count)

        beta = (alpha_complement * _total_not_fake) / total_fake
        beta_complement = _total_fake

        return alpha, alpha_complement, beta, beta_complement

    def predict(self, id_news):
        """
        Classifies news based on ICS
        """

        usersWhichSharedTheNews = self.dao.get_users_which_shared_the_news(id_news)

        productAlphaN = 1.0
        productUmAlphaN = 1.0
        productBetaN = 1.0
        productUmBetaN = 1.0

        for _, row in usersWhichSharedTheNews.iterrows():
            productAlphaN = productAlphaN * row["probalphan"]
            productUmBetaN = productUmBetaN * row["probumbetan"]

        # Bayesian Inference
        reputation_news_tn = (self.omega * productAlphaN * productUmAlphaN) * 100
        reputation_news_fn = ((1 - self.omega) * productBetaN * productUmBetaN) * 100

        if reputation_news_tn >= reputation_news_fn:
            return 0  # notícia classificada como legítima.
        else:
            return 1  # notícia classificada como fake.
