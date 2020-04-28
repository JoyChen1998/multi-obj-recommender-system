import random as rand
import yaml
import pandas as pd
import utils.DataScrawler as scrawl
import os
import logging as log

basic_config_path = 'options/train/config.yml'  # use basic config

class render:
    def __init__(self):
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        #######################
        # loading config
        #######################
        self.train_f_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_f_file_name']
        self.train_p_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_p_file_name']
        self.problem_file = data['datasets']['root'] + data['datasets']['problemset_name']
        self.problem_r_file = data['datasets']['root'] + data['datasets']['problemset_ratio_name']
        self._train_f_df = pd.DataFrame(pd.read_csv(self.train_f_file))
        self._train_p_df = pd.DataFrame(pd.read_csv(self.train_p_file))
        self._p_r_df = pd.DataFrame(pd.read_csv(self.problem_r_file))
        self.contest_root = data['datasets']['data_root']
        ## set logger
        self.logger = log.getLogger()
        self.logger.setLevel(log.INFO)  # Log等级总开关
        log_path = data['log_path']
        log_name = data['log_name']
        log_fullpath = log_path + log_name
        fh = log.FileHandler(log_fullpath, mode='a')
        fh.setLevel(log.DEBUG)
        formatter = log.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    @staticmethod
    def getProblemRandom(plist, getnum):
        """
        return a recommend problem list with random sequence.
        :param plist: total number of problems we have.
        :param getnum: number of problems
        :return: random recommend problems
        """
        return rand.sample(plist, getnum)

    def getOriginContestId(self):
        """
        get current max oj-contest id
        :return: current max oj-contest id <int>
        """
        maxfilename = 0
        for root, dirs, files in os.walk(self.contest_root):
            # print(root) #当前目录路径
            # print(dirs) #当前路径下所有子目录
            for i in range(len(files)):
                if files[i] != '.DS_Store':  # in macOS special file
                    maxfilename = max(int(files[i].rstrip('.csv')), maxfilename)
        return maxfilename

    def getProblemsByLevel(self):
        """
        group by any level problem.
        :return: a list of every level set of problems
        """
        data_df = self._p_r_df
        problem_l1 = []
        problem_l2 = []
        problem_l3 = []
        problem_l4 = []
        problem_l5 = []
        problem_l6 = []
        problem_l7 = []
        problem_l8 = []
        problem_level = []
        for i in range(len(data_df)):
            if data_df['level'][i] == 1:
                problem_l1.append(data_df['id'][i])
            elif data_df['level'][i] == 2:
                problem_l2.append(data_df['id'][i])
            elif data_df['level'][i] == 3:
                problem_l3.append(data_df['id'][i])
            elif data_df['level'][i] == 4:
                problem_l4.append(data_df['id'][i])
            elif data_df['level'][i] == 5:
                problem_l5.append(data_df['id'][i])
            elif data_df['level'][i] == 6:
                problem_l6.append(data_df['id'][i])
            elif data_df['level'][i] == 7:
                problem_l7.append(data_df['id'][i])
            elif data_df['level'][i] == 8:
                problem_l8.append(data_df['id'][i])
        problem_level.append(problem_l1)
        problem_level.append(problem_l2)
        problem_level.append(problem_l3)
        problem_level.append(problem_l4)
        problem_level.append(problem_l5)
        problem_level.append(problem_l6)
        problem_level.append(problem_l7)
        problem_level.append(problem_l8)
        return problem_level







