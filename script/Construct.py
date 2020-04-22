import pandas as pd
import numpy as np
import yaml
import logging as log

basic_config_path = 'options/train/config.yml'  # use basic config

class Construct:
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
        self.problem_file = data['datasets']['root'] + data['datasets']['problemset_name']
        self.problem_r_file = data['datasets']['root'] + data['datasets']['problemset_ratio_name']
        self._train_df = pd.DataFrame(pd.read_csv(self.train_file))
        self._train_f_df = pd.DataFrame(pd.read_csv(self._train_f_df))
        self._gen_df = pd.DataFrame(pd.read_csv(self.genrtate_file))
        self._usr_df = pd.DataFrame(pd.read_csv(self.userinfo_file))
        self._p_df = pd.DataFrame(pd.read_csv(self.problem_file))
        self._p_r_df = pd.DataFrame(pd.read_csv(self._p_r_df))
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

    def construct_factors(self):
        """
        get a factor for each user ,the `factor` is the recognition of their ability.
        include `problem solved` & `AC ratio`

        """
        print('Construct -- construct_factors')
        train_df = self._train_df  # include all data from gen_df & user_df
        gen_df = self._gen_df  # include contest_solved & A to J problems solutions.
        usr_df = self._usr_df  # include Solved, Submit, AC, WA, TLE etc. info.
        only_problem_df = pd.DataFrame(gen_df, columns=['id', 'user', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])
        only_attr_df = pd.DataFrame.merge(pd.DataFrame(gen_df, columns=['id', 'user', 'contestSolved']),
                                          pd.DataFrame(usr_df, columns=['user', 'Solved', 'Submit', 'AC', 'WA']))
        classes = np.unique(train_df['user'].apply(str).apply(lambda x: x[:10]).tolist())
        multiple_factors = [0.68, 0.7, 0.8, 0.9, 1.0, 1.1, 1.5, 2.5, 3.5]
        # difficulty factors in user, to judge user's ability

        # generate 3 attribute for training data
        user_p = []
        for rows in train_df.values:
            user_param = 0
            for i in range(len(multiple_factors)):
                user_param += multiple_factors[i] * rows[9 + i]
            if rows[7] != 0:
                user_param *= (rows[6]/rows[5])
            else:
                user_param = 0
            user_p.append(user_param)
        # add factor to estimate user's ability
        train_df['factor'] = user_p
        columns = ['id', 'user', 'nickname', 'factor', 'Solved',
                   'contestSolved', 'Submit', 'AC', 'WA', 'TLE',
                   'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        try:
            train_df.to_csv(self.train_f_file, index=False, columns=columns)  # save calc factors
            print('generate', self.train_f_file, 'successfully!')
        except Exception:
            print('failed to factor -> csv ', Exception)

    def construct_problem_ratio(self):
        """
        calc the problems' ratio, add to its origin csv.
        """
        print('Construct -- construct_problem_ratio')
        p_df = self._p_df
        acr = []
        lv = []
        for rows in p_df.values:
            ac=rows[3]
            sub=rows[4]
            if ac and sub:
                _ac = round(float(ac) / float(sub), 3)
            else:
                _ac = 0
            acr.append(_ac)
            lv.append(getLevel_p(_ac, sub))
        p_df['ac_ratio'] = acr
        p_df['level'] = lv
        columns= ['num', 'id', 'name', 'level', 'ac', 'submit', 'ac_ratio']
        try:
            p_df.to_csv(self.problem_r_file, index=False, columns=columns)  # save ac ratio
            print('generate',  self.problem_r_file, 'successfully!')
        except Exception:
            print('failed to ac ratio -> csv', Exception)

def getLevel_p(e, s):
    l = 1  ## init problem level
    if 0 < e <= 0.2 and s < 500:
        l = 8
    elif 0 < e <= 0.2 and s > 500:
        l = 7
    elif 0.2 < e <= 0.4 and s < 500:
        l = 6
    elif 0.2 < e <= 0.4 and s > 500:
        l = 5
    elif 0.4 < e <= 0.7 and s < 500:
        l = 4
    elif 0.4 < e <= 0.7 and s > 500:
        l = 3
    elif 0.7 < e and s < 500:
        l = 2
    elif 0.7 < e and s > 500:
        l = 1
    return l





