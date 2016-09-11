# coding = UTF-8

import jieba
from collections import Counter

file = open(r'D:\data\test\government.txt', encoding='UTF-8')
content = file.read()

# 利用结巴分词，精确模式
seg_list = jieba.cut(content, cut_all=False)

cou = Counter(seg_list)
for item in cou.most_common(100):
    if len(item[0]) > 1:
        print(item)