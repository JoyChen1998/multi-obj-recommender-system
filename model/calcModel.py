import math
import yaml
import numpy as np
import pandas as pd
import utils.util as utl
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

basic_config_path = 'options/train/config.yml'  # use basic config

class calcModel:
    def __init__(self):
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        #######################
        # loading config
        #######################
        self.dir_path = data['datasets']['data_root']
        self.genrtate_file = data['datasets']['generate_csv_root'] + data['datasets']['generate_file_name']
        self.userinfo_file = data['datasets']['generate_csv_root'] + data['datasets']['generate_userinfo_name']
        self.train_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_file_name']
        self.train_f_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_f_file_name']
        self.train_prefer_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_p_file_name']
        self.problem_file = data['datasets']['root'] + data['datasets']['problemset_name']
        self.problem_r_file = data['datasets']['root'] + data['datasets']['problemset_ratio_name']
        self._train_df = pd.DataFrame(pd.read_csv(self.train_file))
        self._gen_df = pd.DataFrame(pd.read_csv(self.genrtate_file))
        self._usr_df = pd.DataFrame(pd.read_csv(self.userinfo_file))
        self._p_df = pd.DataFrame(pd.read_csv(self.problem_file))

    def kmeans_clustering_user(self, grade):
        """
        this clustering is for user's favorites, but not for their ability.
        ability decides to their factors.
        :param grade: [str] list
        """
        estimator = KMeans(n_clusters=8)
        # cluster for 5 classes. ensure user's level.
        data_df = self._train_df
        user = []
        lastone = []
        lasttwo = []
        lastthree = []
        lastfour = []
        new_df = pd.DataFrame(columns=['user', 'lastOne', 'lastTwo', 'lastThree', 'lastFour'])
        for g in range(len(grade)):
            for i in range(len(data_df)):
                if '7000' > str(data_df['user'][i])[4:8] > '1000' and str(data_df['user'][i])[:4] == grade[g]:
                    user.append(data_df['user'][i])
                    lastone.append(data_df['J'][i])
                    lasttwo.append(data_df['I'][i])
                    lastthree.append(data_df['H'][i])
                    lastfour.append(data_df['G'][i])
        new_df['user'] = user
        new_df['lastOne'] = lastone
        new_df['lastTwo'] = lasttwo
        new_df['lastThree'] = lastthree
        new_df['lastFour'] = lastfour
        estimator.fit(new_df[['lastOne', 'lastTwo', 'lastThree', 'lastFour']])

        label_pred = estimator.labels_  # 获取聚类标签
        ####### 绘制k-means结果
        print(label_pred)
        x0 = new_df[label_pred == 0]
        x1 = new_df[label_pred == 1]
        x2 = new_df[label_pred == 2]
        x3 = new_df[label_pred == 3]
        x4 = new_df[label_pred == 4]
        x5 = new_df[label_pred == 5]
        x6 = new_df[label_pred == 6]
        x7 = new_df[label_pred == 7]

        plt.scatter(x0.values[:, -1], x0.values[:, -2], label='0-class')
        plt.scatter(x1.values[:, -1], x1.values[:, -2], label='1-class')
        plt.scatter(x2.values[:, -1], x2.values[:, -2], label='2-class')
        plt.scatter(x3.values[:, -1], x3.values[:, -2], label='3-class')
        plt.scatter(x4.values[:, -1], x4.values[:, -2], label='4-class')
        plt.scatter(x5.values[:, -1], x5.values[:, -2], label='5-class')
        plt.scatter(x6.values[:, -1], x6.values[:, -2], label='6-class')
        plt.scatter(x7.values[:, -1], x7.values[:, -2], label='7-class')
        plt.legend(loc='best')
        plt.title(' status', fontsize=12)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.xlabel('last2prob', fontsize=12)
        plt.ylabel('last1prob', fontsize=12)
        plt.show()
        ####### plot test end

        ##############
        # make tags
        ##############
        data_df['prefer_class'] = [0] * len(data_df)
        for i in x0.values:
            data_df.loc[data_df['user'] == i[0], ['prefer_class']] = 0
        for i in x1.values:
            data_df.loc[data_df['user'] == i[0], ['prefer_class']] = 1
        for i in x2.values:
            data_df.loc[data_df['user'] == i[0], ['prefer_class']] = 2
        for i in x3.values:
            data_df.loc[data_df['user'] == i[0], ['prefer_class']] = 3
        for i in x4.values:
            data_df.loc[data_df['user'] == i[0], ['prefer_class']] = 4
        for i in x5.values:
            data_df.loc[data_df['user'] == i[0], ['prefer_class']] = 5
        for i in x6.values:
            data_df.loc[data_df['user'] == i[0], ['prefer_class']] = 6
        for i in x7.values:
            data_df.loc[data_df['user'] == i[0], ['prefer_class']] = 7

        self._prefer_df = data_df

    def saveTo_csv(self):
        columns = ['id', 'user', 'nickname', 'Solved', 'prefer_class',
                   'contestSolved', 'Submit', 'AC', 'WA', 'TLE',
                   'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self._prefer_df.to_csv(self.train_prefer_file, index=False, columns=columns)
        print('generate train_prefer_class.csv successfully!')
















