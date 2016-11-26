# coding=UTF-8

"""
=========================================
区域匹配类
=========================================

:Author: glen
:Date: 2016.10.26
:Tags: region
:abstract: 对区域进行匹配

**类**
==================
RegionMatcher
    区域匹配类

**使用方法**
==================

**示范代码**
==================

"""

import re
from libs.imexport.class_mongodb import MongoDB,MonDatabase,MonCollection
from libs.imexport.class_Excel import Excel
import regex
import pandas as pd


class RegionMatcher:
    def __init__(self, region_query=None):
        # 设置查询结果
        if region_query is None:
            mongo = MongoDB()
            mdb = MonDatabase(mongodb=mongo, database_name='region')
            collection = MonCollection(database=mdb, collection_name='admincode')
            self.collection = collection.collection
        else:
            self.collection = region_query

        self.collection = None

    def match(self,regions=None,year=None):
        pass


class RegionMatchingAlgorithm:
    def __init__(self,to_be_matched=None):
        self._to_be_matched = to_be_matched


class RegionMatchingOrderAlgorithm(RegionMatchingAlgorithm):
    """ 顺序匹配算法类

    :param pandas.DataFrame to_be_matched: 待匹配的区域数据框
    :param pandas.DataFrame to_be_compared: 标准的区域数据框
    :return: 无返回值
    """
    def __init__(self,to_be_matched=None,to_be_compared=None):
        RegionMatchingAlgorithm.__init__(self,to_be_matched=to_be_matched)
        self._to_be_compared = to_be_compared
        # 结果保存在_result变量中
        self._result = None

    def correct(self,correction='auto'):
        if isinstance(collection,dict):
            pass
        else:
            if re.match('^auto$',correction):
                correction = self.auto_correction()
            else:
                correction = pd.read_excel(correction)

        is_index_rid = False

        if correction.index.name == 'rid':
            is_index_rid = True

        if 'rid' in correction.columns:
            correction = correction.set_index('rid')
            is_index_rid = True

        if is_index_rid:
            for ind in correction.index:
                self._result.loc[ind,'region'] = correction.loc[ind,'matched']
        else:
            correction_dict = dict([(correction.loc[ind,'region'],correction.loc[ind,'matched']) for ind in correction.index])
            for ind in RegionMatchingOrderAlgorithm.not_matched(self._result).index:
                if self._result.loc[ind,'region'] in correction_dict:
                    self._result.loc[ind,'region'] = correction_dict[self._result.loc[ind,'region']]

    @property
    def simu_auto_corrected_region_list(self):
        correction = self.auto_correction()

        if correction.size > 0:
            corr_result = pd.merge(self._result,self._to_be_compared[['cid','region']],how='left',on='cid')
            corr_result = corr_result.rename(columns={'region_x':'region','region_y':'compared'})
            corr_result['supplement'] = None

            for ind in correction.index:
                corr_result.loc[ind,'compared'] = correction.loc[ind,'matched']
                corr_result.loc[ind,'acode'] = correction.loc[ind,'acode']
                corr_result.loc[ind,'cid'] = correction.loc[ind,'cid']
                corr_result.loc[ind,'supplement'] = self.output_of_region_set_mapping.loc[ind,'matching_regions']

        del corr_result['_id']

        return corr_result

    @property
    def simu_auto_corrected_region_list_short_version(self):
        select_index = set()
        for num in sorted(self.region_set_dict):
            select_index.update([max(0,num-1),num,min(algo._result.shape[0]-1,num+1)])

        result = self.simu_auto_corrected_region_list.loc[sorted(list(select_index)),]

        return result

    def find_anchor(self,type='merge'):
        """ 寻找锚，即发现区域列表中确定匹配的区域（点）

        :param str type: 定锚算法类型：merge（用pandas.DataFrame的merge定锚）
        :return: 修改_result，无返回值
        """
        if re.match('^merge$',type) is not None:
            self._result = self._merge_matching()

    @property
    def region_set_mapping(self):
        """ 定锚之后，生成缺失区域的参考区域选择映射

        :return: 返回映射
        """
        not_matched = RegionMatchingOrderAlgorithm.not_matched(self._result)
        all_matched = RegionMatchingOrderAlgorithm.all_matched(self._result)

        refer_regions_map = []
        for i in not_matched.index:
            region = not_matched.loc[i]['region']
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

    def auto_correction(self,error='auto'):
        """ 返回自动纠错匹配结果

        :param error: 允许错误数量
        :return: 返回自动纠错匹配结果
        """
        correction = []
        map = self.region_set_mapping
        for record in map:
            region = record[0]
            index = record[1]
            refer_regions = record[2]
            for n in range(len(refer_regions)):
                if self.fuzzy_region_matching(region,refer_regions[n]['region'],error):
                    correction.append([region,index,refer_regions[n]['region'],refer_regions[n]['acode'],refer_regions[n]['cid']])

        correction = pd.DataFrame(correction,columns=['region','rid','matched','acode','cid'])
        correction = correction.set_index('rid')

        return correction

    def exactly_matching_from_region_set(self):
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
                    self._result.loc[index,'acode'] = refer_regions[n]['acode']
                    self._result.loc[index,'cid'] = refer_regions[n]['cid']
                    self._result.loc[index,'_id'] = refer_regions[n]['_id']
                    break

    @staticmethod
    def fuzzy_region_matching(region,compared,error='auto'):
        if re.match('^auto$',error) is not None:
            error = max(1,int(len(region)*0.4))

        return regex.fullmatch('(?:%s){e<=%s}' % (region, str(error)),compared) is not None

    def _merge_matching(self):
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
        merge_result = pd.merge(self._to_be_matched, self._to_be_compared, how='left', on='region')
        merge_result = merge_result.drop_duplicates(subset='rid',keep=False)

        #merge_result = pd.merge(self._to_be_matched,merge_result,how='left',on='rid')
        #del merge_result['region_y']

        return merge_result.rename(columns={'region_x':'region'})

    @property
    def accuracy(self):
        accuracy = 100*(RegionMatchingOrderAlgorithm.all_matched(self._result).shape[0]/(self._result.shape[0]))
        return accuracy

    @staticmethod
    def not_matched(pdata=None):
        return pdata[pdata.isnull().any(axis=1)]

    @staticmethod
    def all_matched(pdata=None):
        return pdata[pdata.notnull().all(axis=1)]

    @property
    def region_set_dict(self):
        ref_regions_dict = dict()
        for record in self.region_set_mapping:
            to_be_selected = []
            for item in record[2]:
                to_be_selected.append(item['region'])
            ref_regions_dict[record[1]] = to_be_selected
        return ref_regions_dict

    @property
    def matched_region(self):
        return self._result


if __name__ == '__main__':
    pop_year = '2010'
    pop_region_file_2010 = r'E:\data\popcensus\origin\var_temp.xls'
    raw_region_2010 = Excel(pop_region_file_2010).read()
    to_be_matched = [re.sub('\s+','',item[0]) for item in raw_region_2010 if re.match('^\s*$',item[0]) is None]
    pd_to_be_matched = pd.DataFrame(to_be_matched,columns=['region'])
    pd_to_be_matched['rid'] = range(pd_to_be_matched.shape[0])

    collection = MonCollection(database=MonDatabase(mongodb=MongoDB(), database_name='region'), collection_name='admincode')
    found = collection.collection.find(filter={'year':'2010'},
                                       projection={'acode':True,'region':True,'_id':True},
                                       sort=[('acode',1)])

    pd_to_be_compared = pd.DataFrame(list(found))
    pd_to_be_compared['cid'] = range(pd_to_be_compared.shape[0])
    #pd_to_be_compared['_id'] = pd_to_be_compared['_id'].apply(str)

    print(pd_to_be_matched,pd_to_be_compared)
    algo = RegionMatchingOrderAlgorithm(pd_to_be_matched,pd_to_be_compared)
    # 首先是寻找可靠的匹配作为锚点
    algo.find_anchor()
    # 其次进行顺序的严格匹配
    algo.exactly_matching_from_region_set()
    print(algo.matched_region)
    # 打印匹配率
    print('Accuracy Rate: {:.2f}%.'.format(algo.accuracy))

    '''
    # 纠正错误
    #algo.correct(correction=r'E:\data\popcensus\origin\correction.xlsx')
    algo.auto_correction().to_excel(r'E:\data\popcensus\origin\correction.xlsx')
    #algo.matched_region.to_excel(r'E:\data\popcensus\origin\pdoutput_before.xlsx')
    algo.correct()

    # 重新进行匹配
    algo.exactly_matching_from_region_set()
    print('Accuracy Rate: {:.2f}%.'.format(algo.accuracy))

    # 输出匹配完成的结果
    algo.matched_region.to_excel(r'E:\data\popcensus\origin\pdoutput.xlsx')

    algo.output_of_region_set_mapping.to_excel(r'E:\data\popcensus\origin\reference_regions.xlsx')

    print(algo.auto_correction())
    algo.auto_correction().to_excel(r'E:\data\popcensus\origin\correction.xlsx')
    print(algo.auto_correction().size)
    algo.simu_auto_corrected_region_list.to_excel(r'E:\data\popcensus\origin\sim_output.xlsx')
    algo.simu_auto_corrected_region_list_short_version.to_excel(r'E:\data\popcensus\origin\sim_output_short.xlsx')

    result.to_excel(r'E:\data\popcensus\origin\pdoutput.xlsx')

    cor_file = r'E:\data\popcensus\origin\correction.xlsx'
    pdata = pd.read_excel(cor_file)
    print(pdata)

    '''
