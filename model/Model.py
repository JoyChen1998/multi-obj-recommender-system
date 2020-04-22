import yaml
import pandas as pd
import script.render as render
import logging as log

basic_config_path = 'options/train/config.yml'  # use basic config


class Model:
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
        self.train_prefer_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train'][
            'train_p_file_name']
        self.problem_file = data['datasets']['root'] + data['datasets']['problemset_name']
        self.problem_r_file = data['datasets']['root'] + data['datasets']['problemset_ratio_name']
        self.problem_num = data['recommend_problem']
        self._train_f_df = pd.DataFrame(pd.read_csv(self.train_f_file))
        self._gen_df = pd.DataFrame(pd.read_csv(self.genrtate_file))
        self._usr_df = pd.DataFrame(pd.read_csv(self.userinfo_file))
        self._p_df = pd.DataFrame(pd.read_csv(self.problem_file))
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


    def getUsersParamsNProblems(self, uid):
        user = {
            'uid': uid,
            'nickname': None,
            'factor': None,
            'submit': None,
            'prefer_class': None,
            'get_recommend': None
        }
        r = render.render()
        user_info = r.getUser(uid)
        user['nickname'] = user_info['nickname']
        user['submit'] = user_info['submit']
        user['prefer_class'] = user_info['prefer_class']
        user['factor'] = user_info['factor']
        ## get all problem for this factor
        problem = r.getProblemByFactor(factor=user['factor'])
        ## set user's recommend problems
        user['get_recommend'] = r.getProblemRandom(problem, self.problem_num)
        return user



