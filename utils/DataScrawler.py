import pandas as pd
import hashlib
import yaml
import time
import requests as r
from bs4 import BeautifulSoup as bs
import utils.util as utl
import csv
import logging as log

basic_config_path = 'options/train/config.yml'  # use basic config

user_status = {
    "user": None,
    "Solved": None,
    "Submit": None,
    "AC": None,
    "WA": None,
    "TLE": None,
    "OLE": None
}


def transform(e):
    if e.isdigit():
        return int(e)
    else:
        return 0


def check(e):
    if e is None:
        return 0
    else:
        return int(e)


def pwdmd5(str):
    h = hashlib.md5()
    h.update(str.encode(encoding='utf-8'))
    return h.hexdigest()


class DataScrawler:
    def __init__(self):
        # load config
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        self.login_url = data['oj_login_url']
        self.down_contest_url1 = data['oj_contest_down_url']
        self.down_contest_url2 = data['oj_contest_down2_url']
        self.latestAC_url = data['oj_user_latestAC_url']
        self.contest_url = data['oj_contest_url']
        self.user_info_url = data['oj_user_info_url']
        self.csv_dir = data['datasets']['data_root']
        self.file = data['datasets']['generate_csv_root'] + data['datasets']['generate_file_name']
        self.tmp_file = data['datasets']['generate_csv_root'] + data['datasets']['generate_tmp_file_name']
        self.userinfo_file = data['datasets']['generate_csv_root'] + data['datasets']['generate_userinfo_name']
        login_id = data['oj_username']
        passwd = data['oj_passwd']
        # load end
        self.contest_start = 0
        self.contest_end = 0
        self.s = r.session()
        self.login_data = {
            'user_id': login_id,
            'password': passwd,
            'vcode': 'ZHEliSHIqianQIANzhuanSHUdeZIfu'
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us",
            "Connection": "keep-alive",
            "Accept-Charset": "GB2312,utf-8;q=0.7,*;q=0.7"
        }
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

    def login(self):
        try:
            self.s.post(self.login_url, data=self.login_data)
            print('login ok!')
        except Exception:
            print('login failed with', Exception)

    def get_contest(self, start_id, end_id):
        """
        get contest from OJ , just rank info.

        :param start_id: get contest from this id
        :param end_id: get contest end up this id

        """
        print('totally need to finish', end_id - start_id, 'tasks.')
        pbar = utl.ProgressBar(task_num=(end_id-start_id))
        for i in range(start_id, end_id):
            pbar.update()
            time.sleep(1)
            try:
                self.req = self.s.get(self.down_contest_url1 + str(i)).content
            except:
                try:
                    self.req = self.s.get(self.down_contest_url2 + str(i)).content
                except:
                    self.logger.warning('CALL DataScrawler -> get_contest -> getContest error! maybe this id '+ str(i) + ' is expired!')

            req = self.req.decode('utf-8')  # chars transfer to Chinese
            html = bs(req, 'lxml')
            try:
                title = html.find('center').text
                html_data = pd.read_html(req)
            except Exception:
                self.logger.warning(str(i)+'\tdoesn\'t exist!')
                continue
            for j in html_data:
                table = pd.DataFrame(j)
                table.to_csv(self.csv_dir + str(i) + '.csv', encoding='utf-8', index=False, header=False)
                # must add header=False, or will append a useless line
                self.logger.info(str(i) + '\t' + str(title) + ' saves successfully!')

    def get_train_data(self):
        """

        !!! important: this function must run after data processing -> generate.csv !!!
        ----------------------------------------------------------------------------------
        I have got a problem that I can't down all data at once. Because the server may bans my ip
        (maybe I `get` the server too many times at a short time) , so I could lost the conn.
        In order to keep these data, I have to save them into a file, and keep append data, again and again.

        """
        global user_status
        df = pd.DataFrame(pd.read_csv(self.tmp_file))      # get new student data from generate_tmp.csv , then I need to combine 2 generate.csv
        pbar = utl.ProgressBar(task_num=len(df))
        columns = ['user', 'Solved', 'Submit', 'AC', 'WA', 'TLE', 'OLE']

        # create a file to save the user's info data.
        with open(self.userinfo_file, 'a') as f:       # change mode w -> a , update on 23/4/2020 , modified on run.
            dict_writer = csv.DictWriter(f, fieldnames=columns)
            dict_writer.writeheader()
        # create end
        for num in range(len(df)):
            pbar.update()
            try:
                req = self.s.get(self.user_info_url + str(df['user'][num]), headers=self.headers)
            except Exception:
                self.logger.warning('CALL DataScrawler -> get_train_data -> get user info error.. ')
                continue
            time.sleep(0.5)
            info = bs(req.content, 'lxml').find_all("td")
            so = su = ac = wa = tle = ole = None
            for i in range(len(info)):
                if info[i].text == 'AC':
                    ac = transform(info[i + 1].text.strip())
                elif info[i].text == 'WA':
                    wa = transform(info[i + 1].text.strip())
                elif info[i].text == 'TLE':
                    tle = transform(info[i + 1].text.strip())
                elif info[i].text == 'OLE':
                    ole = transform(info[i + 1].text.strip())
                elif info[i].text == 'Solved':
                    so = transform(info[i + 1].text.strip())
                elif info[i].text == 'Submit':
                    su = transform(info[i + 1].text.strip())
            user_status = {
                "user": df['user'][num],
                "Solved": check(so),
                "Submit": check(su),
                "AC": check(ac),
                "WA": check(wa),
                "TLE": check(tle),
                "OLE": check(ole)
            }

            # keep append data into the file
            with open(self.userinfo_file, 'a') as f:
                dict_writer = csv.DictWriter(f, fieldnames=columns)
                dict_writer.writerow(user_status)

    def getUserLatestACProblems(self, ulist):
        """
        get a ac problems list by users' list `have same prefer class` .
        !!! best : it would be better use db , ip will not be banned. !!!
        :param ulist: user's list
        :return: user's ac problems list(set) , [int]
        """
        ac_p = set()
        pbar = utl.ProgressBar(task_num=len(ulist))
        for i in range(len(ulist)):
            time.sleep(0.5)
            pbar.update()
            try:
                req = self.s.get(self.latestAC_url + str(ulist[i]), headers=self.headers)
                t = bs(req.content, 'lxml')
                tbody = t.find('table').find('tbody').find_all('tr')
                for i in tbody:
                    p = i.find_all('td')[2].text
                    ac_p.add(int(p))
            except Exception:
                continue
        return list(ac_p)

    def getLatestContestId(self):
        """
        find the Online Judge contest latest contest id.
        :return: the latest contest id [int]
        """
        req = self.s.get(self.contest_url, headers=self.headers)
        content = bs(req.content, 'lxml')
        id = content.find('table').find('tbody').find('tr').find('td')
        return int(id.text.strip())
