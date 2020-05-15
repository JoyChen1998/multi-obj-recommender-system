import threading
import yaml
import csv
import logging as log
import time
import pymysql as msql
import pandas as pd
import model.calcModel as calcmodel
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
cons = construct.Construct()
calcmm = calcmodel.calcModel()
up = update.updateData()


def checkDB():
    """
    check the db conn status.
    """
    host = data['db_host']
    user = data['db_user']
    passwd = data['db_pass']
    dbname = data['db_name']
    try:
        db = msql.connect(host, user, passwd, dbname)
        db.close()
        return True
    except:
        logger.error('Can\'t connect to the database!')
        return False

def updateInfo():
    """
    update info include => {
        update latest contest id                    => call srcawler
        get origin contest id                       => call render
        create contest_csv/xxxx.csv                 => call scrawler
        create generate_csv/generate.csv
        create generate_csv/user_Info.csv
        combine generate/*.csv -> train.csv (basic train set)
        create problem.csv                          => call scrawler   *
        calculate train_factor.csv by train.csv     => call Construct
        calculate problem_r.csv by problem.csv      => call Construct  *
        update statistic images                     => call iplot
    }
    """

    ##########################
    ## update basic datasets
    ##########################
    scrawl.login()
    latestId = scrawl.getLatestContestId()
    originId = rend.getOriginContestId()
    logger.info('get new update --> origin_id =', originId, ' , the latest_id =', latestId)
    scrawl.get_contest(originId + 1, latestId)  # create contest_csv/xxxx.csv
    dprocess.preprocess_contest(originId + 1, latestId)
    dprocess.generate_tmp_csv()
    scrawl.get_train_data()  # get user basic train data from generate_tmp.csv,
    dprocess.combine2generate_csv()  # then combine 2 generate.csv
    dprocess.merge_2dfNgenerate_train_data()  # need to change a merge function

    # image plot
    # idraw.plot_class_with_line(['2016585011', '2016585012', '2016585031', '2017585011'], 10)
    # idraw.plot_train_lst2problem_scatters('2016')

    ###########################
    ## update factors & ratios
    ###########################
    cons.construct_factors()
    cons.construct_problem_ratio()
    calcmm.kmeans_clustering_user(['2014', '2015', '2016', '2017', '2018', '2019'])


def getRecent_problems():
    """
    get all student recent solved problems record.
    !! need to save the data, necessary!  Also,due to the OJ server always bans my IP . !!
    """
    ########################################
    ## get recent problems to recommendation
    ########################################
    txt_save_path = data['tmp_problem_path']
    train_p_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_p_file_name']
    train_p_df = pd.DataFrame(pd.read_csv(train_p_file))
    # get recent user solved record
    for i in range(0, 8):
        tmp_df = train_p_df[train_p_df['prefer_class'].isin([i])]
        li = tmp_df['user'].tolist()
        problems = scrawl.getUserLatestACProblems(li)
        ### save get problems
        with open(txt_save_path + str(i) + '_problem.txt', 'w') as f:
            for x in range(len(problems)):
                f.write(str(problems[x]) + ',')
        logger.info(txt_save_path + str(i) + '_problem.txt write succeed!')
        f.close()
    logger.info('get recent problems succeed!')


def makeRecommendation():
    csv_name = data['datasets']['recommendation_name']
    csv_path = data['datasets']['root']
    train_p_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_p_file_name']
    train_p_df = pd.DataFrame(pd.read_csv(train_p_file))
    csv_f = csv_path + csv_name
    problems = rend.getProblemsByLevel()
    rec_prob = []
    user_all = []
    pl1 = problems[0]
    pl2 = problems[1]
    pl3 = problems[2]
    pl4 = problems[3]
    pl5 = problems[4]
    prop = [0.8, 0.6, 0.4, 0.2, 0.1]  # with probability for system recommendation.
    rec_prob0 = _getTmp(0)
    rec_prob1 = _getTmp(1)
    rec_prob2 = _getTmp(2)
    rec_prob3 = _getTmp(3)
    rec_prob4 = _getTmp(4)
    rec_prob5 = _getTmp(5)
    rec_prob6 = _getTmp(6)
    rec_prob7 = _getTmp(7)

    rec_prob.append(rec_prob0)
    rec_prob.append(rec_prob1)
    rec_prob.append(rec_prob2)
    rec_prob.append(rec_prob3)
    rec_prob.append(rec_prob4)
    rec_prob.append(rec_prob5)
    rec_prob.append(rec_prob6)
    rec_prob.append(rec_prob7)

    for i in range(len(train_p_df)):
        user = {
            'uid': None,
            'nick': None,
            'factor': None,
            'solved': None,
            'prefer_cls': None,
            'get_recom': None
        }
        sys_problem = []
        uid = train_p_df['user'][i]
        nickname = train_p_df['nickname'][i]
        solved = train_p_df['Solved'][i]
        factor = train_p_df['factor'][i]
        prefer_class = train_p_df['prefer_class'][i]
        user['uid'] = uid
        user['nick'] = nickname
        user['solved'] = solved
        user['factor'] = factor
        user['prefer_cls'] = prefer_class
        if cons.is_newBee(factor):
            user['get_recom'] = rend.getProblemRandom(pl1 + pl2, data['recommend_num'])
        else:
            if 30 < factor <= 60:
                sys_problem = rend.getProblemRandom(pl2 + pl3, int(data['recommend_num'] * prop[0]))
            elif 60 < factor <= 80:
                sys_problem = rend.getProblemRandom(pl3 + pl4, int(data['recommend_num'] * prop[1]))
            elif 80 < factor <= 100:
                sys_problem = rend.getProblemRandom(pl4 + pl5, int(data['recommend_num'] * prop[2]))
            elif 100 < factor <= 110:
                sys_problem = rend.getProblemRandom(pl4 + pl5, int(data['recommend_num'] * prop[3]))
            remain = data['recommend_num'] - len(sys_problem)
            user_recom = sys_problem + rend.getProblemRandom(rec_prob[prefer_class], remain)
            user['get_recom'] = list(user_recom)
        user_all.append(user)

    with open(csv_f, 'w') as ff:
        w = csv.DictWriter(ff, user_all[0].keys())
        w.writeheader()
        for i in range(len(user_all)):
            w.writerow(user_all[i])
    ff.close()
    logger.info('make recommendation finished!')


def run():
    if not checkDB():
        logger.error('can not connect to the DB, program halted!')
        exit(0)

    while True:
        if not up.checkTime():
            time.sleep(5)
        else:
            # do multi-threading {}
            updateInfo()  # update info & cluster user data
            getRecent_problems() # get user's recent problems
            makeRecommendation() 
            up.updateDB() # save recommendation to db


def _getTmp(e):
    path = data['tmp_problem_path']
    file1 = path + str(e) + '_problem.txt'
    with open(file1, 'r') as f:
        total = f.readline()  # only one line
        problems_list = total.split(',')[:-1]
    for i in range(len(problems_list)):
        problems_list[i] = int(problems_list[i])
    return problems_list


def read_recommendation_df_test():
    df = pd.DataFrame(pd.read_csv('data/recommendation.csv'))
    l = df['get_recom'][0].lstrip('[').rstrip(']').split(', ')

run()