import argparse
import sys
import utils.DataScrawler as ds
username = ''
passwd = ''

dataSource = ds.DataScrawler(username, passwd)
dataSource.login()
dataSource.getcontest(1600, 1605)


