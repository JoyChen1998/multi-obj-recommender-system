import yaml
import pandas as pd
import logging as log
import pymysql as msql
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
        self.recommendation = data['datasets']['root'] + data['datasets']['recommendation_name']
        self._train_f_df = pd.DataFrame(pd.read_csv(self.train_f_file))
        self._p_r_df = pd.DataFrame(pd.read_csv(self.problem_r_file))
        self._recom_df = pd.DataFrame(pd.read_csv(self.recommendation))
        self.host = data['db_host']
        self.user = data['db_user']
        self.passwd = data['db_pass']
        self.dbname = data['db_name']
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
        sql_create = """CREATE TABLE IF NOT EXISTS `rs` (
                          `uid` BIGINT DEFAULT NULL,
                          `factor` float DEFAULT NULL,
                          `solved` int(11) DEFAULT NULL,
                          `prefer_cls` int(11) DEFAULT NULL,
                          `get_recom` varchar(100) DEFAULT NULL
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
        sql_clear = "DELETE FROM `rs`"
        df = self._recom_df
        db = msql.connect(self.host, self.user, self.passwd, self.dbname)
        cursor = db.cursor()
        try:
            # create & clear table `rs`
            cursor.execute(sql_create)
            cursor.execute(sql_clear)
        except:
            self.logger.error('create db table failed')
            return False

        ###############
        # insert data
        ###############
        for i in range(len(df)):
            d_uid = df['uid'][i]
            d_factor = df['factor'][i]
            d_solved = df['solved'][i]
            d_prefer_cls = df['prefer_cls'][i]
            d_get_recom = df['get_recom'][i]
            sql = "INSERT INTO rs(uid, factor, solved, prefer_cls, get_recom) VALUES ('%s', '%s', '%s', '%s', '%s')" % \
                  (d_uid, d_factor, d_solved, d_prefer_cls, d_get_recom)
            try:
                # 执行sql语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
            except:
                # 如果发生错误则回滚
                self.logger.error('insert recommendation data into table failed')
                db.rollback()
                return False
        self.logger.info('update database succeed!')
        db.close()
        return True






