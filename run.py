import threading
import yaml
import logging as log
import time
import os
import requests as r
import model.calcModel as calcmodel
import model.Model as mmodel
import script.render as render
import script.Construct as construct
import script.updateData as update
import utils.DataScrawler as scrawler
import utils.InfoPlot as iplot
import utils.DataProcesser as processer
import utils.util as utl

basic_config_path = 'options/train/config.yml'  # use basic config

with open(basic_config_path, 'r', encoding='utf-8') as f:
    data = yaml.load(f.read())

# set logger
logger = log.getLogger()
logger.setLevel(log.INFO)  # Log等级总开关
log_path = data['log_path']
log_name = data['log_name']
log_fullpath = log_path + log_name
fh = log.FileHandler(log_fullpath, mode='a')
fh.setLevel(log.DEBUG)
formatter = log.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

scrawl = scrawler.DataScrawler()
rend = render.render()
dprocess = processer.DataProcesser()
idraw = iplot.InfoPlot()

def checkDB():
    """
    check the db conn status.
    """
    return True


def updateInfo():
    """
    update info include => {
        update latest contest id                    => call srcawler
        get origin contest id                       => call render
        create contest_csv/xxxx.csv                 => call scrawler
        create generate_csv/generate.csv
        create generate_csv/user_Info.csv
        combine generate/*.csv -> train.csv (basic train set)
        create problem.csv                          => call scrawler   /haven't did
        calculate train_factor.csv by train.csv     => call Construct
        calculate problem_r.csv by problem.csv      => call Construct  /haven't did
        update statistic images                     => call iplot
    }
    """
    scrawl.login()
    latestId = scrawl.getLatestContestId()
    originId = rend.getOriginContestId()
    scrawl.get_contest(originId+1, latestId)   # create contest_csv/xxxx.csv
    dprocess.preprocess_contest(originId+1, latestId)
    dprocess.generate_csv()
    # scrawl.get_train_data()                  # need to set a scrawl user id.
    # dprocess.merge_2dfNgenerate_train_data() # need to change a merge function

    #image plot
    # idraw.plot_class_with_line(['2016585011', '2016585012', '2016585031', '2017585011'], 10)
    # idraw.plot_train_lst2problem_scatters('2016')

def run():
    if not checkDB():
        logger.error('can not connect to the DB, program halted!')
        exit(0)
    updateInfo()




def runTime():
    up = update.updateData()
    while True:
        if not up.checkTime():
            time.sleep(5)
        else:
            # do multi-threading {}
            up.updateUserCluster([''])
            up.updateDB()


# pool = [
#     threading.Thread(target=run),
#     threading.Thread(target=runTime)
# ]

# for t in pool:
#     t.start()


