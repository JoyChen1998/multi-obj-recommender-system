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
        #######################
        # loading config
        #######################
        self.file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_file_name']
        self.f_file = data['datasets']['train']['train_csv_root'] + data['datasets']['train']['train_f_file_name']
        self.plot_save = data['plot_save']
        self.plot_path = data['plot_save_path']
        self.df = pd.DataFrame(pd.read_csv(self.file))
        self.f_df = pd.DataFrame(pd.read_csv(self.f_file))
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

    def plot_grade(self, grade):
        """
        plot a grade's students' `solved`,`submit`, `ac`,`wa`, and calc the ac ratio
        :param grade: the number of grade that need to be ploted. [str]
        """
        data_df = self.df
        sets = np.unique(data_df['user'].apply(str).apply(lambda x: x[4:8]).tolist())
        length = len(sets)
        print(length, type(sets))
        print('get grade', grade)
        _ac = 0
        _sub = 0
        st = set()
        plt.figure(figsize=(30, 15))
        for j in range(length):
            user = []
            solve = []
            submit = []
            ac = []
            wa = []
            for rows in data_df.values:
                if str(rows[1])[:4] == grade and str(rows[1])[10:12] < '55' \
                        and str(rows[1])[4:8] == str(sets[j]) \
                        and str(rows[1])[4] != '0' and str(rows[1])[4] < '7':
                    _ac += rows[6]
                    _sub += rows[3]
                    user.append(str(rows[1])[4:])
                    st.add(str(rows[1])[4:8])
                    solve.append(rows[3])
                    submit.append(rows[5])
                    ac.append(rows[6])
                    wa.append(rows[7])
                    plt.title(grade + '\'s figure')
                    plt.plot(user, solve, label='solve', marker='+')
                    plt.plot(user, submit, label='submit')
                    plt.plot(user, ac, label='ac')
                    plt.plot(user, wa, label='wa')
                    plt.xticks(fontsize=20)
                    plt.yticks(fontsize=20)
            # _ac_ratio = _ac / _sub
        print('starting plot!')
        plt.savefig(self.plot_path + 'plot_grade-' + str(grade) + '.jpg')
        plt.show()

    def plot_class_with_line(self, plot_class, length):
        """
        plot class's `score`, `AC`, `problems of contest solved`.
        use origin plot style.
        :param plot_class: classes need to plot , [list]
        :param length: show class's number length, example: '2016585011' => length=10

        """
        data_df = self.df
        plot_len = math.ceil(float(len(plot_class) / 2))  # get subplot columns, and rows => 2
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
                j.append(data_df['user'][i] - int(plot_class[x]) * pow(10, 12 - length))
                jscore.append(data_df['Solved'][i])
                jac.append(data_df['AC'][i])
                jsub.append(data_df['Submit'][i])
                jconsolved.append(data_df['contestSolved'][i])
            plt.subplot(plot_len, 2, x + 1)
            plt.xlim((0, 55))
            plt.title(plot_class[x][length - 2:length] + ' class\'s figure', fontsize=20)
            plt.plot(j, jscore, label='score')
            plt.plot(j, jac, label='ac')
            plt.plot(j, jsub, label='submit')
            plt.plot(j, jconsolved, label='contest', marker='+')
            plt.xticks(fontsize=20)
            plt.yticks(fontsize=20)
            plt.legend(loc='best')
        if self.plot_save:
            plt.savefig(self.plot_path + 'plot_class_with_line-' + "class.jpg")
        plt.show()

    def plot_stu_with_pie(self, stu):
        """
        plot stu's ability and which kind of problems they can solved
        :param stu: stu to plot, [list]
        """
        data_df = self.df
        labels_pie = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        labels_hist = ['Solved', 'contestSolved', 'Submit', 'AC', 'WA', 'TLE']
        plt.figure(figsize=(10, 5 * len(stu)))
        index = 1
        for x in range(len(stu)):
            for row in data_df.values:
                if str(row[1]) == stu[x]:
                    stu_info = row[3:9]
                    pie_info = row[9:]
                    print(stu_info, '\n', pie_info)
                    plt.subplot(len(stu), 2, index)
                    plt.title(str(stu[x])[-4:] + '\'s ability')
                    bar_df = pd.DataFrame({"x-axis": labels_hist, "y-axis": stu_info})
                    sns.barplot("x-axis", "y-axis", palette="RdBu_r", data=bar_df)
                    index += 1
                    plt.subplot(len(stu), 2, index)
                    plt.title(str(stu[x])[-4:] + '\'s problems')
                    plt.xticks(fontsize=20)
                    plt.yticks(fontsize=20)
                    print(len(pie_info), len(labels_pie))
                    plt.pie(x=pie_info, labels=labels_pie)
                    index += 1
                else:
                    continue
        if self.plot_save:
            plt.savefig(self.plot_path + 'plot_stu-' + "students.jpg")
        plt.show()

    def plot_trainSet_factors_scatters(self, grade):
        """
        plot the `grade` distribution map of `factor` & `solved problems`

        :param grade:the number of grade [int]
        """
        data_df = self.f_df
        solved = []
        factor = []
        user = []
        jksolved = []
        jkfactor = []
        new_df = pd.DataFrame(columns=['user', 'solved', 'factor'])
        for rows in data_df.values:
            if str(rows[1])[2:4] == str(grade) and '700' > str(rows[1])[4:7] > '100':
                if str(rows[1])[4:8] == '5850':
                    jkfactor.append(rows[3])
                    jksolved.append(rows[4])
                user.append(int(str(rows[1])[4:9]))
                factor.append(rows[3])
                solved.append(rows[4])
        new_df['user'] = user
        new_df['solved'] = solved
        new_df['factor'] = factor
        sns.lmplot(x='solved', y='factor', data=new_df, hue='user', height=12, fit_reg=False)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.xlabel('Solved', fontsize=20)
        plt.ylabel('Factor', fontsize=20)
        plt.savefig(self.plot_path + 'scatter' + str(grade) + '.jpg')
        plt.show()
