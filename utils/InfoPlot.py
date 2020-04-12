import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import yaml
import seaborn as sns

basic_config_path = 'options/train/config.yml'  # use basic config


class InfoPlot:
    def __init__(self):
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        self.file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_file_name']
        self.plot_save = data['plot_save']
        self.plot_path = data['plot_save_path']
        self.df = pd.DataFrame(pd.read_csv(self.file))
        sns.set_style('whitegrid')
        plt.style.use('seaborn-white')

    def plot_scatter(self):

        ######################
        #  prepare data
        ######################
        data_df = self.df
        # get classes from user[:9] -> str
        self.classes = np.unique(data_df['user'].apply(str).apply(lambda x: x[:8]).tolist())
        classes_list = self.classes.tolist()
        self.solved = [0 for i in range(len(self.classes))]  # initial solved list
        self.contest_solved = [0 for i in range(len(self.classes))]  # initial contest_solved list
        for i in range(len(data_df['user'])):
            index = classes_list.index(str(data_df['user'][i])[:8])  # get user's class -> index
            self.solved[index] += data_df['Solved'][i]
            self.contest_solved[index] += data_df['contestSolved'][i]
        for i in range(len(self.classes)):
            self.classes[i] = int(self.classes[i])
        classes = self.classes

        #############################
        #  draw plot for each class
        #############################
        solved = self.solved
        contest_solved = self.contest_solved

        print(classes, '\n', type(classes), 'len=', len(classes))
        print(solved, '\n', type(solved), ' len=', len(solved))
        plt.figure(figsize=(20, 10), dpi=80, facecolor='w', edgecolor='k')
        plt.scatter(classes, solved)
        plt.show()

    def plot_hist(self):
        data_df = self.df
        # user = np.unique(data_df['user'].apply(str).apply(lambda x: x[:6]).tolist())
        user14 = []
        user15 = []
        user16 = []
        user17 = []
        user18 = []
        u14 = []
        u15 = []
        u16 = []
        u17 = []
        u18 = []
        for i in range(len(data_df['user'])):
            if str(data_df['user'][i])[:4] == '2014':
                user14.append(data_df['Solved'][i])
                u14.append(data_df['user'][i])
            elif str(data_df['user'][i])[:4] == '2015':
                user15.append(data_df['Solved'][i])
                u15.append(data_df['user'][i])
            elif str(data_df['user'][i])[:4] == '2016':
                user16.append(data_df['Solved'][i])
                u16.append(data_df['user'][i])
            elif str(data_df['user'][i])[:4] == '2017':
                user17.append(data_df['Solved'][i])
                u17.append(data_df['user'][i])
            elif str(data_df['user'][i])[:4] == '2018':
                user18.append(data_df['Solved'][i])
                u18.append(data_df['user'][i])

        plt.figure(num=1, figsize=(16, 9))
        plt.plot(u14, user14, label='14')
        plt.figure(num=2)
        plt.plot(u15, user15, label='15')
        plt.figure(num=3)
        plt.plot(u16, user16, label='16')
        plt.figure(num=4)
        plt.plot(u17, user17, label='17')
        plt.show()

    def plot_class_with_line(self, plot_class, length):
        """
        plot class's `score`, `AC`, `problems of contest solved`.
        use origin plot style.
        :param plot_class: classes need to plot , [list]
        :param length: show class's number length, example: '2016585011' => length=10

        """
        data_df = self.df
        plot_len = math.ceil(float(len(plot_class)/2))  # get subplot columns, and rows => 2
        plt.figure(figsize=(20, 10))
        for x in range(len(plot_class)):
            j = []
            jscore = []
            jac = []
            jsub = []
            jconsolved = []
            for i in range(len(data_df)):
                if str(data_df['user'][i])[:length] < plot_class[x] or str(data_df['user'][i])[10:12] > '55':
                    # skip  and reach plot class.
                    continue
                if str(data_df['user'][i])[:length] != plot_class[x]:
                    break
                j.append(data_df['user'][i] - int(plot_class[x])*pow(10, 12-length))
                jscore.append(data_df['Solved'][i])
                jac.append(data_df['AC'][i])
                jsub.append(data_df['Submit'][i])
                jconsolved.append(data_df['contestSolved'][i])
            plt.subplot(plot_len, 2, x+1)
            plt.xlim((0, 55))
            plt.title(plot_class[x][length-2:length] + ' class\'s figure')
            plt.plot(j, jscore, label='score')
            plt.plot(j, jac, label='ac')
            plt.plot(j, jsub, label='sub')
            plt.plot(j, jconsolved, label='contest', marker='+')
            plt.legend()
        plt.show()