import pandas as pd
import numpy as np
import yaml

basic_config_path = 'options/train/config.yml'  # use basic config


class Construct:
    def __init__(self):
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        self.dir_path = data['datasets']['data_root']
        self.genrtate_file = data['datasets']['generate_csv_root'] + data['datasets']['generate_file_name']
        self.userinfo_file = data['datasets']['generate_csv_root'] + data['datasets']['generate_userinfo_name']
        self.train_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_file_name']
        self.train_f_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_f_file_name']
        self._train_df = pd.DataFrame(pd.read_csv(self.train_file))
        self._gen_df = pd.DataFrame(pd.read_csv(self.genrtate_file))
        self._usr_df = pd.DataFrame(pd.read_csv(self.userinfo_file))

    def construct_factors(self):
        """
        get a factor for each user ,the `factor` is the recognition of their ability.
        include `problem solved` & `AC ratio`

        """
        train_df = self._train_df  # include all data from gen_df & user_df
        gen_df = self._gen_df  # include contest_solved & A to J problems solutions.
        usr_df = self._usr_df  # include Solved, Submit, AC, WA, TLE etc. info.
        only_problem_df = pd.DataFrame(gen_df, columns=['id', 'user', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])
        only_attr_df = pd.DataFrame.merge(pd.DataFrame(gen_df, columns=['id', 'user', 'contestSolved']),
                                          pd.DataFrame(usr_df, columns=['user', 'Solved', 'Submit', 'AC', 'WA']))
        classes = np.unique(train_df['user'].apply(str).apply(lambda x: x[:10]).tolist())
        multiple_factors = [0.68, 0.7, 0.8, 0.9, 1.0, 1.1, 1.5, 2.5, 3.5]
        # difficulty factors in user, to judge user's ability
        user_p = []
        for rows in train_df.values:
            user_param = 0
            for i in range(len(multiple_factors)):
                user_param += multiple_factors[i] * rows[9 + i]
            if rows[7] != 0:
                user_param *= (rows[6]/rows[5])
            else:
                user_param = 0
            user_param = round(user_param, 3)
            user_p.append(user_param)
        train_df['factor'] = user_p  # add factor to estimate user's ability
        columns = ['id', 'user', 'nickname', 'factor', 'Solved',
                   'contestSolved', 'Submit', 'AC', 'WA', 'TLE',
                   'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        try:
            train_df.to_csv(self.train_f_file, index=False, columns=columns)  # save calc factors
            print('generate ', self.train_f_file, ' successfully!')
        except Exception:
            print('failed to factor -> csv ', Exception)

        q1 = []
        q2 = []
        q3 = []
        q4 = []

        for rows in train_df.values:
            print(rows[0], rows[1], rows[2], rows[3])
            if 0 < rows[3] < 50:
                q1.append(rows[1])
            elif 50 <= rows[3] < 80:
                q2.append(rows[1])
            elif 80 <= rows[3] < 110:
                q3.append(rows[1])
            elif rows[3] >= 110:
                q4.append(rows[1])







