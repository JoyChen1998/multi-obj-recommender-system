import random as rand
import yaml
import numpy as np
import pandas as pd
import utils.util as utl
import requests as r

basic_config_path = 'options/train/config.yml'  # use basic config

class render:
    def __init__(self):
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        #######################
        # loading config
        #######################
        self.train_f_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_f_file_name']
        self.problem_file = data['datasets']['root'] + data['datasets']['problemset_name']
        self.problem_r_file = data['datasets']['root'] + data['datasets']['problemset_ratio_name']
        self._train_f_df = pd.DataFrame(pd.read_csv(self.train_f_file))
        self._p_r_df = pd.DataFrame(pd.read_csv(self.problem_r_file))

    def getUser(self, uid):
        data_df = self._train_f_df
        user = {
            'uid': None,
            'nickname': None,
            'factor': None,
            'submit': None,
            'prefer_class': None
        }
        for i in range(len(data_df)):
            if str(data_df['user'][i]) == uid:
                user['uid'] = data_df['user'][i]
                user['nickname'] = data_df['nickname'][i]
                user['factor'] = data_df['factor'][i]
                user['submit'] = data_df['submit'][i]
                user['prefer_class'] = data_df['prefer_class'][i]
                break
        return user

    def getProblemByFactor(self, factor):
        problem_df = self._p_r_df
        if 0 < factor < 40:
            p_recom =1
        elif 40 < factor < 70:
            p_recom =3
        elif 70 < factor < 100:
            p_recom =5
        else:
            p_recom =7
        p_list = []
        for i in range(len(problem_df)):
            if problem_df['level'] == p_recom:
                p_list.append(problem_df['id'])
        return p_list

    @staticmethod
    def getProblemRandom(plist, getnum):
            return rand.sample(plist, getnum)







