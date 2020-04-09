import argparse
import sys
import utils.DataScrawler as ds
import utils.DataProcesser as dpr

if __name__ == '__main__':
    a = dpr.DataProcesser()
    a.preprocess_contest(1500, 2504)
    a.generate_csv()