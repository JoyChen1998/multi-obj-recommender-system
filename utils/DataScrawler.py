import pandas as pd
import hashlib
import yaml
import time
from bs4 import BeautifulSoup as bs
import requests as r

basic_config_path = 'options/train/config.yml'  # use basic config


def pwdmd5(str):
    h = hashlib.md5()
    h.update(str.encode(encoding='utf-8'))
    return h.hexdigest()


class DataScrawler:
    def __init__(self):
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        self.login_url = data['oj_login_url']
        self.down_contest_url1 = data['oj_contest_down_url']
        self.down_contest_url2 = data['oj_contest_down2_url']
        self.csv_dir = data['datasets']['train']['data_root']
        login_id = data['oj_username']
        passwd = data['oj_passwd']
        self.contest_start = 0
        self.contest_end = 0
        self.s = r.session()
        self.login_data = {
            'user_id': login_id,
            'password': passwd,
            'vcode': 'ZHEliSHIqianQIANzhuanSHUdeZIfu'
        }

    def login(self):
        try:
            self.s.post(self.login_url, data=self.login_data)
            print('login ok!')
        except Exception:
            print('login failed with', Exception)

    def getcontest(self, start_id, end_id):
        """
        get contest from OJ , just rank info.

        :param start_id: get contest from this id
        :param end_id: get contest end up this id
        """
        for i in range(start_id, end_id):
            time.sleep(1)
            try:
                self.req = self.s.get(self.down_contest_url1 + str(i)).content
            except:
                try:
                    self.req = self.s.get(self.down_contest_url2 + str(i)).content
                except:
                    print('getContest info error! maybe this id ', i, ' is expired !')

            req = self.req.decode('utf-8')      # chars transfer to Chinese
            html = bs(req, 'lxml')
            try:
                title = html.find('center').text
                html_data = pd.read_html(req)
            except Exception:
                print(i, '\tdoesn\'t exist!')
                continue

            for j in html_data:
                table = pd.DataFrame(j)
                table.to_csv(self.csv_dir + str(i) + '.csv', encoding='utf-8', index=False, header=False)
                # must add header=False, or will append a useless line
                print(i, '\t', title, ' ok!')