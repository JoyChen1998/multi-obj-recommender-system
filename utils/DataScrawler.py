import pandas as pd
import hashlib
import yaml
import time
import requests as r
from bs4 import BeautifulSoup as bs
import utils.DataProcesser as dtp
import utils.util as utl


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
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        self.login_url = data['oj_login_url']
        self.down_contest_url1 = data['oj_contest_down_url']
        self.down_contest_url2 = data['oj_contest_down2_url']
        self.user_info_url = data['oj_user_info_url']
        self.csv_dir = data['datasets']['train']['data_root']
        self.train_file = data['datasets']['train']['generate_csv_root'] + data['datasets']['train']['train_file_name']
        self.file = data['datasets']['train']['generate_csv_root'] + data['datasets']['train']['generate_file_name']
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
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us",
            "Connection": "keep-alive",
            "Accept-Charset": "GB2312,utf-8;q=0.7,*;q=0.7"
        }


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
        print('totally need to finish', end_id-start_id, 'tasks.')
        self.pbar = utl.ProgressBar()
        for i in range(start_id, end_id):
            self.pbar.update()
            time.sleep(1)
            try:
                self.req = self.s.get(self.down_contest_url1 + str(i)).content
            except:
                try:
                    self.req = self.s.get(self.down_contest_url2 + str(i)).content
                except:
                    print('getContest info error! maybe this id ', i, ' is expired !')

            req = self.req.decode('utf-8')  # chars transfer to Chinese
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
                print(i, '\t', title, ' saves successfully!')

    def get_train_data(self):
        global user_status
        processor = dtp.DataProcesser()
        l = []
        df = pd.DataFrame(pd.read_csv(self.file))
        self.pbar = utl.ProgressBar(task_num=len(df))
        for num in range(len(df)):
            self.pbar.update()
            req = self.s.get(self.user_info_url + str(df['user'][num]), headers=self.headers)
            time.sleep(1.5)
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
            l.append(user_status)
        df2 = pd.DataFrame(l)
        processor.merge_2dfNgenerate_train_data(df, df2)

