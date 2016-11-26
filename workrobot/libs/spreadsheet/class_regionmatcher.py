# coding = UTF-8


"""
=========================================
区域匹配类
=========================================

:Author: glen
:Date: 2016.11.14
:Tags: region match
:abstract: 区域匹配类

**类**
==================
RegionMatcher
    区域匹配类

**使用方法**
==================

**示范代码**
==================

"""

import os
import re
import pandas as pd
from dbadmin.admindivision.class_admindivision import AdminDivision


class RegionMatcher:
    """ 类RegionMatcher是区域匹配类

    """
    def __init__(self, to_be_matched=None, year=None, top_level=1, down_level=2):
        self._to_be_matched = to_be_matched.rename(columns={'region': 'origin'})
        self._to_be_matched['region'] = to_be_matched.applymap(lambda x: re.sub('\s+','',x))
        self._to_be_matched['rid'] = range(self._to_be_matched.shape[0])

        self._admin_division = AdminDivision(year=year)

        self._top_level = top_level
        if top_level == 1:
            if down_level == 1:
                self._to_be_compared = self._admin_division.province
            elif down_level == 2:
                self._to_be_compared = self._admin_division.province_and_prefecture
            else:
                self._to_be_compared = self._admin_division.all_region
        elif top_level == 2:
            if down_level == 2:
                self._to_be_compared = self._admin_division.prefecture
            else:
                self._to_be_compared = self._admin_division.prefecture_and_county
        else:
            self._to_be_compared = self._admin_division.county
        self._to_be_compared = self._to_be_compared[['region','acode']]
        self._to_be_compared['cid'] = range(self._to_be_compared.shape[0])
        self._to_be_compared.index = range(self._to_be_compared.shape[0])

    def place_anchor(self,type='match'):
        """ 寻找锚，即发现区域列表中确定匹配的区域（点）

        :param str type: 定锚算法类型：merge（用pandas.DataFrame的merge定锚）
        :return: 修改_result，无返回值
        """
        if re.match('^merge$',type) is not None:
            self._result = self.place_anchor_by_merging()
        if re.match('^match$',type) is not None:
            self._result = self.place_anchor_by_matching()

    def place_anchor_by_matching(self):
        region_found = set()
        for ind in self._to_be_matched.index:
            if self._top_level == 1:
                found = self._admin_division.get_province(self._to_be_matched.loc[ind,'region'])
            elif self._top_level == 2:
                found = self._admin_division.get_prefecture(self._to_be_matched.loc[ind, 'region'])
            elif self._top_level == 3:
                found = self._admin_division.get_county(self._to_be_matched.loc[ind, 'region'])
            else:
                print('unknown level!')
                raise Exception
            if found.shape[0] > 0:
                if found.shape[0] < 2:
                    if found['region'].values[0] not in region_found:
                        self._to_be_matched.loc[ind, 'acode'] = found['acode'].values[0]
                        region_found.add(found['region'].values[0])

        return self.place_anchor_by_merging(on='acode')

    def place_anchor_by_merging(self,how='left',on='region'):
        """ 定锚，通过merge进行匹配
        完成时self._result对象为pandas.DataFrame
        	   region	mid	acode  cid
            0	北京市	0	110000	0
            1	市辖区	1
            2	东城区	2	110101	2
            3	西城区	3	110102	3

        :return: 无返回值
        """
        # 返回初次定锚的对象：pandas.DataFrame
        merge_result = pd.merge(self._to_be_matched, self._to_be_compared, how=how, on=on)
        merge_result = merge_result.drop_duplicates(subset='rid', keep=False)

        return merge_result.rename(columns={'{}_x'.format(on): on,'region_x':'region','region_y':'matched'})

    def matching_using_region_set(self):
        """ 从备选区域集中选择区域，用精确匹配

        :return: 无返回值
        """
        map = self.region_set_mapping
        for record in map:
            region = record[0]
            index = record[1]
            refer_regions = record[2]
            for n in range(len(refer_regions)):
                if re.match(region,refer_regions[n]['region']) is not None:
                    self._result.loc[index,'matched'] = refer_regions[n]['region']
                    self._result.loc[index,'acode'] = refer_regions[n]['acode']
                    self._result.loc[index,'cid'] = refer_regions[n]['cid']
                    break

    def matching_using_correction(self,correction):
        if os.path.isfile(correction):
            file_data = pd.read_excel(correction)
            column = file_data.columns[0]
            for ind in file_data.index:
                found_region = self._admin_division[file_data.loc[ind,'replace']]
                self._result.loc[file_data.loc[ind,column]==self._result[column],column] = file_data.loc[ind,'replace']
                print(self._result.loc[file_data.loc[ind,'replace']==self._result[column], 'matched'],found_region['region'].values[0])
                self._result.loc[file_data.loc[ind,'replace']==self._result[column], 'matched'] = found_region['region'].values[0]
                self._result.loc[file_data.loc[ind,'replace']==self._result[column], 'acode'] = found_region['acode'].values[0]
        elif isinstance(correction,dict):
            pass
        else:
            print('Unknown Type of Correction: ',type(correction))
            raise Exception

    @property
    def region_set_mapping(self):
        """ 定锚之后，生成缺失区域的参考区域选择映射

        :return: 返回映射
        """
        not_matched = RegionMatcher.not_matched(self._result)
        all_matched = RegionMatcher.all_matched(self._result)

        refer_regions_map = []
        for i in not_matched.index:
            region = not_matched.loc[i]['region']
            search_start = 0
            search_end = self._to_be_compared.shape[0]
            # 锚定上下文位置
            for m in range(i,-1,-1):
                if m in all_matched.index:
                    search_start = int(all_matched.loc[m]['cid'])
                    break
            for m in range(i,self._result.shape[0]):
                if m in all_matched.index:
                    search_end = int(all_matched.loc[m]['cid'])
                    break
            # 可选择的区域
            if re.match('石家庄',region):
                print(self._to_be_matched.loc[3])
            refer_regions = [self._to_be_compared.loc[n] for n in range(search_start+1,search_end)]
            # 构建映射：列表——每个元素为(区域名称，位置，可选择的匹配区域)
            refer_regions_map.append((region,i,refer_regions))
        return refer_regions_map

    @property
    def output_of_region_set_mapping(self):
        """ 返回区域选择映射

        :return: 返回区域选择映射
        """
        result = []
        for record in self.region_set_mapping:
            result.append([record[0],record[1],','.join([item['region'] for item in record[2]])])

        result = pd.DataFrame(result,columns=['region','rid','matching_regions'])
        result = result.set_index('rid')
        return result

    @property
    def accuracy(self):
        accuracy = 100*(RegionMatcher.all_matched(self._result).shape[0]/(self._result.shape[0]))
        return accuracy

    @staticmethod
    def not_matched(pdata=None):
        return pdata[pdata.isnull().any(axis=1)]

    @staticmethod
    def all_matched(pdata=None):
        return pdata[pdata.notnull().all(axis=1)]

    @property
    def matched_region(self):
        return self._result

if __name__ == '__main__':
    #rmatcher = RegionMatcher()
    file = r'E:\data\citystat\transform\replace.xls'
    print(os.path.isfile(file))
    file_data = pd.read_excel(file)
    columns = list(file_data.columns.values)
    print(type(columns))
    print(file_data.columns[0])


