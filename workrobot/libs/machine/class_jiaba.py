# coding=UTF-8

"""
=========================================
中文分词 —— 结巴分词
=========================================

:Author: glen
:Date: 2016.8.23
:Tags: jiaba
:abstract: 用结巴分词进行中文分词

**类**
==================
WordSegmentation
    用结巴分词进行中文分词


**使用方法**
==================


**示范代码**
==================

"""

import jieba
from collections import Counter


class WordSegmentation:
    def __init__(self, content):
        self._words = jieba.cut(content, cut_all=False)
        self._words_counter = Counter(self._words)

    @property
    def words(self):
        return list(self._words)

    @property
    def counter(self):
        return self._words_counter


if __name__ == '__main__':
    file = open(r'D:\data\test\news.txt', encoding='UTF-8')
    content = file.read()

    seg = WordSegmentation(content)
    for item in seg.counter.most_common(100):
        if len(item[0]) > 1:
            print(item)