import pandas as pd
import hashlib
from bs4 import BeautifulSoup as bs
import requests as r


def pwdmd5(str):
    h = hashlib.md5()
    h.update(str.encode(encoding='utf-8'))
    return h.hexdigest()


class DataScrawler:
    def __init__(self, login_id, passwd):
        self.login_data = {
            'user_id': login_id,
            'password': passwd,
            'vcode': 'ZHEliSHIqianQIANzhuanSHUdeZIfu'
        }
        self.login_url = "http://202.194.119.110/login.php"
        self.down_contest_url1 = "http://202.194.119.110/contestrank.xls.php?cid="
        self.down_contest_url2 = "http://202.194.119.110/contestrank2.xls.php?cid="
        self.contest_start = 0
        self.contest_end = 0
        self.csv_dir = 'data/csv/'
        self.s = r.session()

    def login(self):
        try:
            self.s.post(self.login_url, data=self.login_data)
            print('login ok!')
        except Exception:
            print('login failed with', Exception)

    def getcontest(self, start_id, end_id):
        for i in range(start_id, end_id):
            try:
                self.req = self.s.get(self.down_contest_url1 + str(i)).content
            except:
                try:
                    self.req = self.s.get(self.down_contest_url2 + str(i)).content
                except:
                    print('getContest info error! maybe this id ', i, ' is expired !')

            req = self.req.decode('utf-8')      # chars transfer to Chinese
            html = bs(req, 'lxml')
            html_data = pd.read_html(req)
            for j in html_data:
                table = pd.DataFrame(j)
                table.to_csv(self.csv_dir + str(i) + '.csv', encoding='utf-8', index=False, header=False)   # must add header=False, or will append a useless line