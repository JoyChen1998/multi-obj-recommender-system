import pandas as pd
import csv
import operator
import utils.util as utl
import yaml
import logging as log

basic_config_path = 'options/train/config.yml'  # use basic config


def getNum(row, index):
    if len(row) > index and type(row[index]) == str:
        return 1
    else:
        return 0


class DataProcesser:
    def __init__(self):
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        #######################
        # loading config
        #######################
        self.dir_path = data['datasets']['data_root']
        self.file = data['datasets']['generate_csv_root'] + data['datasets']['generate_file_name']
        self.userinfo_file = data['datasets']['generate_csv_root'] + data['datasets']['generate_userinfo_name']
        self.train_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_file_name']
        self.dictlist = []
        self.cmp = operator.itemgetter('user')  # add sort attr
        # add logger
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

    def preprocess_contest(self, start_id, end_id):
        """
        do preprocessing contest.csv ,
        get info 'username', 'nickname', 'amount of `totally solved contest`'

        :param start_id: preprocess start id,
        :param end_id: preprocess end id,
        """
        print('DataProcesser -- preprocess_contest')
        self.pbar = utl.ProgressBar()
        for num in range(start_id, end_id):
            self.pbar.update()
            file_path = self.dir_path + str(num) + '.csv'
            try:
                d = pd.read_csv(file_path)
            except:
                print('do not have', num, '-csv')
                continue
            df = pd.DataFrame(d)
            for row in df.values:
                if len(str(row[1])) != 12 or str(row[1])[0:4] < '2010' or str(row[1])[0:4] > '2019':  # filter dirty info
                    continue
                flag = False
                for i in range(len(self.dictlist)):
                    if int(row[1]) == self.dictlist[i]["user"]:
                        self.update_csv(row, i)
                        flag = True
                if not flag:
                    udict = {
                        "id": 1,
                        "user": int(row[1]),
                        "nickname": row[2],
                        "contestSolved": float(row[3]),
                        "A": float(getNum(row, 5)),
                        "B": float(getNum(row, 6)),
                        "C": float(getNum(row, 7)),
                        "D": float(getNum(row, 8)),
                        "E": float(getNum(row, 9)),
                        "F": float(getNum(row, 10)),
                        "G": float(getNum(row, 11)),
                        "H": float(getNum(row, 12)),
                        "I": float(getNum(row, 13)),
                        "J": float(getNum(row, 14)),
                    }
                    self.dictlist.append(udict)
                    print(udict)
        self.dictlist.sort(key=self.cmp)  # sort by username
        for i in range(len(self.dictlist)):
            self.dictlist[i]['id'] = i + 1

    def update_csv(self, row, index):
        print('DataProcesser -- update csv')
        """
        update csv info, sum which problem user has `solved` in contest

        :param row: current read line
        :param index: user's index in dict_list
        """
        self.dictlist[index]["contestSolved"] += float(row[3])
        self.dictlist[index]["A"] += float(getNum(row, 5))
        self.dictlist[index]["B"] += float(getNum(row, 6))
        self.dictlist[index]["C"] += float(getNum(row, 7))
        self.dictlist[index]["D"] += float(getNum(row, 8))
        self.dictlist[index]["E"] += float(getNum(row, 9))
        self.dictlist[index]["F"] += float(getNum(row, 10))
        self.dictlist[index]["G"] += float(getNum(row, 11))
        self.dictlist[index]["H"] += float(getNum(row, 12))
        self.dictlist[index]["I"] += float(getNum(row, 13))
        self.dictlist[index]["J"] += float(getNum(row, 14))

    def generate_csv(self):
        print('DataProcesser -- generate csv')
        """
        generate a csv & clustering contest info.
        """
        dictlist = self.dictlist
        new_csv_file = self.file
        pbar = utl.ProgressBar(task_num=len(dictlist))
        with open(new_csv_file, 'a') as f:               ## change mode w -> a ,modified by 4/23/2020 on run
            w = csv.DictWriter(f, dictlist[0].keys())
            w.writeheader()
            for i in range(len(dictlist)):
                pbar.update()
                w.writerow(dictlist[i])
        f.close()

    def merge_2dfNgenerate_train_data(self):
        """
        merge genertate.csv & user_info.csv and generate `train.csv`
        """
        print('DataProcesser -- merge_2dfNgenerate_train_data')
        df1 = pd.DataFrame(pd.read_csv(self.file))
        df2 = pd.DataFrame(pd.read_csv(self.userinfo_file))
        df = pd.merge(df1, df2)
        print(df)
        columns = ['id', 'user', 'nickname', 'Solved',
                   'contestSolved', 'Submit', 'AC', 'WA', 'TLE',
                   'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        df.to_csv(self.train_file, index=False, columns=columns)
        print('generate train.csv successfully!')
