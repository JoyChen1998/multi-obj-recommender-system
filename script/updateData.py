import random as rand
import yaml
import numpy as np
import pandas as pd
import utils.util as utl
import model.calcModel as cm
import time


basic_config_path = 'options/train/config.yml'  # use basic config


class updateData:
    def __init__(self):
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        #######################
        # loading config
        #######################
        self.train_f_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_f_file_name']
        self.problem_r_file = data['datasets']['root'] + data['datasets']['problemset_ratio_name']
        self._train_f_df = pd.DataFrame(pd.read_csv(self.train_f_file))
        self._p_r_df = pd.DataFrame(pd.read_csv(self.problem_r_file))

    @staticmethod
    def checkTime():
        """
        check if need to update data.
        :return: bool
        """
        t = time.localtime()
        now_hr = t[2]
        now_min = t[3]
        if now_hr == 12 and now_min < 5:
            return True
        else:
            return False

    @staticmethod
    def updateUserCluster(grade):
        """
        call function -> model/calcModel
        :param grade: grade need to be cluster . [ str ]
        """

        calcmodel = cm.calcModel()
        calcmodel.kmeans_clustering_user(grade)

    def updateDB(self):
        pass

    def updateContest(self, origin, latest):
        pass


