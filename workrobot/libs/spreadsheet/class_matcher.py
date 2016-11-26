# coding=UTF-8

"""
=========================================
匹配类
=========================================

:Author: glen
:Date: 2016.10.26
:Tags: variable
:abstract: 对对象进行匹配

**类**
==================
Matcher
    变量匹配类

**使用方法**
==================

**示范代码**
==================

"""

import re
import regex
import pandas as pd


class Matcher:
    def __init__(self, to_be_matched=None):
        self._to_be_matched = to_be_matched

    def set_to_be_matched(self, to_be_matched=None):
        self._to_be_matched = to_be_matched

    def exact_matching(self, alternative=None):
        if isinstance(alternative,str):
            return re.match(''.join(['^',self._to_be_matched,'$']),alternative) is not None
        elif isinstance(alternative,(tuple,list)):
            for item in alternative:
                if re.match(''.join(['^',self._to_be_matched,'$']),item) is not None:
                    return True
            return False
        else:
            print('Undefined type: ',type(alternative))

    def fuzzy_matching(self, alternative=None, error_percent=0.6):
        error = max(1, int(len(self._to_be_matched) * error_percent))

        return regex.fullmatch('(?:%s){e<=%s}' % (self._to_be_matched, str(error)), alternative)

    def match_to(self,alternatives=None,error_percent=0.6):
        matched = []
        count = []
        for alternative in alternatives:
            if self.fuzzy_matching(alternative,error_percent) is not None:
                matched.append(alternative)
                count.append(sum(self.fuzzy_matching(alternative,error_percent).fuzzy_counts))
        return pd.DataFrame({'origin': self._to_be_matched, 'matched': matched, 'fuzzy_count': count},
                            columns=['origin', 'matched', 'fuzzy_count']).sort_values('fuzzy_count')


class BulkMatcher:
    def __init__(self, to_be_matched=None):
        self._matcher = Matcher()
        self._to_be_matched = to_be_matched

    def exact_matching(self, alternative=None):
        is_matched = []
        for item in self._to_be_matched:
            self._matcher.set_to_be_matched(item)
            if self._matcher.exact_matching(alternative=alternative):
                is_matched.append(True)
            else:
                is_matched.append(False)
        return pd.DataFrame({'origin':self._to_be_matched,'ismatched':is_matched},
                            columns=['origin','ismatched'])

    def fuzzy_matching(self, alternative=None,**kwargs):
        df = []
        for item in self._to_be_matched:
            self._matcher.set_to_be_matched(item)
            df.append(self._matcher.match_to(alternatives=alternative,**kwargs))

        return pd.concat(df)

    def matching(self,alternative=None,type='exact',**kwargs):
        if isinstance(alternative,(tuple,list)):
            if type == 'exact':
                return self.exact_matching(alternative)
            elif type == 'fuzzy':
                return self.fuzzy_matching(alternative,**kwargs)
            else:
                print('Undefined Type: ',type)
        elif isinstance(alternative,dict):
            alternative_keys = list(alternative.keys())
            if type == 'exact':
                pdata = self.exact_matching(alternative_keys)
                mapping = []
                for i in range(pdata.shape[0]):
                    if pdata.iloc[i,pdata.columns.get_loc('ismatched')]:
                        mapping.append(alternative[pdata.iloc[i,pdata.columns.get_loc('origin')]])
                    else:
                        mapping.append(pdata.iloc[i,pdata.columns.get_loc('origin')])
                pdata['mapping'] = mapping
                return pdata
            elif type == 'fuzzy':
                pdata = self.fuzzy_matching(alternative_keys,**kwargs)
                mapping = []
                for i in range(pdata.shape[0]):
                    mapping.append(alternative[pdata.iloc[i, pdata.columns.get_loc('matched')]])
                pdata['mapping'] = mapping
                return pdata
            else:
                print('Undefined Type: ',type)


if __name__ == '__main__':
    matcher = Matcher('上海人民广播电台')
    print(matcher.match_to(['鬼老', '何足道']))
    #print(matcher.match_to(['上海人民电视台','北京人民广播电台','海上民众广播电视台','上海人民广播电台时']))

    bulk_matcher = BulkMatcher(['上海人民广播电台','北京人民广播电台'])
    print(bulk_matcher.exact_matching(['上海人民电视台','北京人民广播电台','海上民众广播电视台','上海人民广播电台时']))

    print(bulk_matcher.fuzzy_matching(['上海人民电视台', '北京人民广播电台', '海上民众广播电视台', '上海人民广播电台时'],error_percent=0.2))

    print(bulk_matcher.matching(alternative={'上海人民广播电台':'华东理工大学',
                                             '北京人民广播电台':'北京大学',
                                             '海上民众广播电视台':'南京大学',
                                             '上海人民广播电台时':'同济大学'},
                                type='exact'))