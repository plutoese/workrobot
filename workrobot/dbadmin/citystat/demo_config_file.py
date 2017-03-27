# coding = UTF-8

import configparser

config = configparser.ConfigParser()
config.read(r'E:\data\citystat\correction\config.ini',encoding='UTF-8')

PATH = config['row_split_fn_param']
for key in PATH:
    print(PATH.get(key,raw=True))
