import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mat
import yaml

basic_config_path = 'options/train/config.yml'  # use basic config


class InfoPlot:
    def __init__(self):
        with open(basic_config_path, 'r', encoding='utf-8') as f:
            data = yaml.load(f.read())
        self.file = data['datasets']['train']['generate_csv_root'] + data['datasets']['train']['generate_file_name']
        self.plot_save = data['plot_save']
        self.plot_path = data['plot_save_path']
        self.df = pd.read_csv(self.file)

    def plot_scatter(self):

        pass

    def plot_pie(self):
        pass

    def plot_hist(self):

        
        pass