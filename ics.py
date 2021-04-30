import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split

from dao.dao import DAO


class ICS:

    def __init__(self, laplace_smoothing=0.01, omega=0.5):

        self.dao = DAO()
        self.news = self.dao.query_news()
        self.users = self.dao.query_users()
        self.news_users = self.dao.query_user_news_relation()
        self.smoothing = laplace_smoothing
        self.omega = omega

    def init_params(self, test_size=0.3):

        # Divide 'self.news' em treino e teste.
        labels = [news["classification"] for news in self.news]
        self.X_train_news, self.X_test_news, _, _ = train_test_split(self.news,
                                                                     labels,
                                                                     test_size=test_size,
                                                                     stratify=labels)

        # # armazena em 'self.train_news_users' as notícias compartilhadas por cada usuário.
        self.train_news_users = pd.merge(self.X_train_news, self.news_users,
                                          left_on="id_news", right_on="id_news")
        self.test_news_users = pd.merge(self.X_test_news, self.news_users,
                                         left_on="id_news", right_on="id_news")

        # conta a qtde de noticias verdadeiras e falsas presentes no conjunto de treino.
        self.not_fake_count = self.news["classification"].value_counts()[0]
        self.fake_count = self.news["ground_truth_label"].value_counts()[1]

        # filtra apenas os usuários que não estão em ambos os conjuntos de treino e teste.
        self.train_news_users = self.train_news_users[
            self.train_news_users["id_social_media_account"].isin(
                self.test_news_users["id_social_media_account"])]

        # inicializa os parâmetros dos usuários.
        totR = 0
        totF = 0
        alphaN = totR + self.smoothing
        umAlphaN = ((totF + self.smoothing) / (self.fake_count + self.smoothing)) * (
            self.not_fake_count + self.smoothing)
        betaN = (umAlphaN * (totR + self.smoothing)) / (totF + self.smoothing)
        umBetaN = totF + self.smoothing
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
        etapa de avaliação: avalia a notícia com base nos parâmetros de cada usuário obtidos na etapa de treinamento.
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

    def fit(self, test_size=0.3):
        """
        Etapa de treinamento: calcula os parâmetros de cada usuário a partir do Implict Crowd Signals.
        """
        i = 0
        self._init_params(test_size)
        users_unique = self.train_news_users["id_social_media_account"].unique()
        total = len(users_unique)

        for userId in users_unique:
            i = i + 1
            print("", end="Progresso do treinamento: {0:.2f}%\r".format(
                float((i / total) * 100)), flush=True)

            # obtém os labels das notícias compartilhadas por cada usuário.
            newsSharedByUser = list(self.train_news_users["ground_truth_label"].loc[
                                        self.train_news_users[
                                            "id_social_media_account"] == userId])

            # calcula a matriz de opinião para cada usuário.
            totR = newsSharedByUser.count(0)
            totF = newsSharedByUser.count(1)
            alphaN = totR + self.smoothing
            umAlphaN = ((totF + self.smoothing) / (
                self.fake_count + self.smoothing)) * (
                           self.not_fake_count + self.smoothing)
            betaN = (umAlphaN * (totR + self.smoothing)) / (totF + self.smoothing)
            umBetaN = totF + self.smoothing

            # calcula as probabilidades para cada usuário.
            probAlphaN = alphaN / (alphaN + umAlphaN)
            probUmAlphaN = 1 - probAlphaN
            probBetaN = betaN / (betaN + umBetaN)
            probUmBetaN = 1 - probBetaN
            self.users.loc[self.users[
                               "id_social_media_account"] == userId, "probAlphaN"] = probAlphaN
            self.users.loc[self.users[
                               "id_social_media_account"] == userId, "probBetaN"] = probBetaN
            self.users.loc[self.users[
                               "id_social_media_account"] == userId, "probUmAlphaN"] = probUmAlphaN
            self.users.loc[self.users[
                               "id_social_media_account"] == userId, "probUmBetaN"] = probUmBetaN

        self._assess()
        return self.users

    def predict(self, id_news):
        """
        Classifica uma notícia usando o ICS.
        """

        usersWhichSharedTheNews = self.dao.get_users_which_shared_the_news(id_news)

        productAlphaN = 1.0
        productUmAlphaN = 1.0
        productBetaN = 1.0
        productUmBetaN = 1.0

        for _, row in usersWhichSharedTheNews.iterrows():
            productAlphaN = productAlphaN * row["probalphan"]
            productUmBetaN = productUmBetaN * row["probumbetan"]

        # inferência bayesiana
        reputation_news_tn = (self.omega * productAlphaN * productUmAlphaN) * 100
        reputation_news_fn = ((1 - self.omega) * productBetaN * productUmBetaN) * 100

        if reputation_news_tn >= reputation_news_fn:
            return 0  # notícia classificada como legítima.
        else:
            return 1  # notícia classificada como fake.
