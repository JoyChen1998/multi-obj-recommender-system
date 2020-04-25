import threading
import yaml
import csv
import logging as log
import time
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
        create problem.csv                          => call scrawler   /haven't done
        calculate train_factor.csv by train.csv     => call Construct
        calculate problem_r.csv by problem.csv      => call Construct  /haven't done
        update statistic images                     => call iplot
    }
    """

    ##########################
    ## update basic datasets
    ##########################
    scrawl.login()
    latestId = scrawl.getLatestContestId()
    originId = rend.getOriginContestId()
    print('get new update --> origin_id =', originId, ' , the latest_id =', latestId)
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


def makeRecommendation():
    ########################################
    ## get all problems to recommendation
    ########################################
    csv_name = data['datasets']['recommendation_name']
    csv_path = data['datasets']['root']
    csv_f = csv_path + csv_name
    problems = rend.getProblemsByLevel()
    pl1 = problems[0]
    pl2 = problems[1]
    pl3 = problems[2]
    pl4 = problems[3]
    pl5 = problems[4]
    train_p_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_p_file_name']
    train_p_df = pd.DataFrame(pd.read_csv(train_p_file))
    user = {
        'uid': None,
        'nick': None,
        'factor': None,
        'solved': None,
        'prefer_cls': None,
        'get_recom': None
    }

    problems_l = []
    # get recent user solved record
    for i in range(0, 8):
        tmp_df = train_p_df[train_p_df['prefer_class'].isin([i])]
        print('get record solved cls->', i, '\n')
        li = tmp_df['user'].tolist()
        print(type(li))
        problems = scrawl.getUserLatestACProblems(li)
        problems_l.append(problems)

    print('get ac problems finished!')
    prop = [0.8, 0.6, 0.4, 0.2, 0.1]
    user_all = []
    for i in range(len(train_p_df)):
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
                sys_problem = rend.getProblemRandom(pl2 + pl3, data['recommend_num'] * prop[0])
            elif 60 < factor <= 80:
                sys_problem = rend.getProblemRandom(pl3 + pl4, data['recommend_num'] * prop[1])
            elif 80 < factor <= 100:
                sys_problem = rend.getProblemRandom(pl4 + pl5, data['recommend_num'] * prop[2])
            elif 100 < factor <= 110:
                sys_problem = rend.getProblemRandom(pl4 + pl5, data['recommend_num'] * prop[3])
            remain = data['recommend_num'] - len(sys_problem)
            user_recom = sys_problem + rend.getProblemRandom(problems_l[prefer_class], remain)
            user['get_recom'] = user_recom
        print(user['uid'], factor, ' --> ', user['get_recom'])
        user_all.append(user)

    with open(csv_f, 'w') as ff:
        w = csv.DictWriter(ff, user_all[0].keys())
        w.writeheader()
        for i in range(len(user_all)):
            w.writerow(user_all[i])
    ff.close()


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

makeRecommendation()
