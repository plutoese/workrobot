# coding=UTF-8

"""
=========================================
admin division数据（行政区划数据接口）
=========================================

:Author: glen
:Date: 2016.11.17
:Tags: mongodb database collection admin division
:abstract: admin division数据接口

**类**
==================
AdminDivision
    admin division数据接口

**使用方法**
==================
admindivision集合接口

# @property:
# - year: 年份
# - version: 版本号
#
# - Province: 所有省份
# - Prefecture: 所有地级地区
# - County：所有县级地区
# - ProvincePrefecture：所有省份和地级地区
# - ProvincePrefectureCounty: 所有省份、地级和县级地区
# @method:
# - getByAcode(self,acode,year)：根据acode和年份得到行政区域，参数acode是行政代码，字符串；year是年份，字符串。
#                                返回数据记录，list。
# - __getitem__(self, key)：重载运算符[]。其中的key表示表示区域名称，方法如下：（1）省级区域，用名字直接表示，
#                           例如ad[u'北京']；    （2）地级区域，用省级、地级名称表示，例如ad[u'浙江',u'嘉兴']；
#                          （3）县级区域，用省级、地级、县级名称表示，例如ad[u'湖北', u'恩施',u'来凤']；（4）
#                           如果是本级行政区域加上下级行政区域，下级行政区域用f（first）表示，例如表示浙江省
#                           及其所有地级行政区域，用ad[u'浙江',u'f']；5）如果是本级行政区域加上下下级行政区域，
#                           下下级行政区域用s（second）表示，例如表示浙江省及其所有县级行政区域，用ad[u'浙江',u's']；
#                         （6）如果是本级行政区域加上下级及下下级行政区域，下级及下下级行政区域用b（both）表示，
#                          例如表示浙江省及其所有地县级行政区域，用ad[u'浙江',u'b']。返回值是数据库中查询得到
#                          的行政区划的列表。

**示范代码**
==================
::

    >>># 连接MongoDB中的ProvinceStat集合
    >>>mongo = MongoDB()
    >>>mdb = MonDatabase(mongodb=mongo, database_name='region')
    >>>prostat = MonDBProvinceStat(database=mdb)
    >>># 返回集合中所有变量列表
    >>>print(prostat.variables)
    >>># 查询变量名
    >>>for item in prostat.search_variable('法人单位数',exact=True).distinct('variable'): print(item)
"""


import re
from dbadmin.admindivision.class_admindivisiondatabase import AdminDivisionDatabase
from pymongo import ASCENDING
import pandas as pd


class AdminDivision:
    """ 类AdminData表示行政区划数据

    :param str,list year: 年份
    :return: 无返回值
    """
    def __init__(self, year=None):
        # 设置数据库
        self.database = AdminDivisionDatabase()

        # 设置版本和年份
        if year is not None:
            if isinstance(year,(int,str)):
                self._year = str(year)
            elif isinstance(year,(tuple,list)):
                self._year = [str(y) for y in year]
        else:
            self._year = None

    def __getitem__(self, key):
        if isinstance(key,str):
            if re.match('^s$',key):
                return self.province
            if re.match('^t$',key):
                return self.prefecture
            if re.match('^f$',key):
                return self.county
            if re.match('^st$',key):
                return self.province_and_prefecture
            if re.match('^sf$',key):
                return self.province_and_county
            if re.match('^tf$',key):
                return self.prefecture_and_county
            if re.match('^stf$',key):
                return self.all_region
            province_found = self.get_province(province=key)
            if province_found.size > 0:
                return province_found
            else:
                prefecture_found = self.get_prefecture(prefecture=key)
                if prefecture_found.size > 0:
                    return prefecture_found
                else:
                    return self.get_county(county=key)

        elif isinstance(key,tuple):
            if len(key) < 2:
                if re.match('^s$', key[0]):
                    return self.province
                if re.match('^t$', key[0]):
                    return self.prefecture
                if re.match('^f$', key[0]):
                    return self.county
                if re.match('^st$', key[0]):
                    return self.province_and_prefecture
                if re.match('^sf$', key[0]):
                    return self.province_and_county
                if re.match('^tf$', key[0]):
                    return self.prefecture_and_county
                if re.match('^stf$', key[0]):
                    return self.all_region
                province_found = self.get_province(province=key[0])

                if province_found.size > 0:
                    return province_found
                else:
                    prefecture_found = self.get_prefecture(prefecture=key[0])
                    if prefecture_found.size > 0:
                        return prefecture_found
                    else:
                        return self.get_county(county=key[0])
            elif len(key) < 3:
                if re.match('^f$', key[1]) is not None:
                    return self.get_prefecture_children(province=key[0])
                if re.match('^s$', key[1]) is not None:
                    return self.get_county_children(province=key[0])
                if re.match('^fs$', key[1]) is not None:
                    return self.get_prefecture_and_county_children(province=key[0])
                found = self.get_prefecture(province=key[0],prefecture=key[1])
                if found.size < 1:
                    found = self.get_county(province=key[0],county=key[1])
                return found
            elif len(key) < 4:
                if re.match('^f$', key[2]) is not None:
                    return self.get_county_children(province=key[0],prefecture=key[1])
                return self.get_county(province=key[0],prefecture=key[1],county=key[2])
            else:
                print('Too many parameters!')
                raise Exception

    def set_year(self,year):
        """ 设置年份

        :param str year: 年份
        :return: 无返回值
        """
        if isinstance(year, (int, str)):
            self._year = str(year)
        elif isinstance(year, (tuple, list)):
            self._year = [str(y) for y in year]

    def get_province(self, province=None):
        """ 获得省级行政区划

        :param str province: 省级行政区划名称
        :return: 返回查询得到的省级行政区划
        :rtype: pandas.DataFrame
        """
        if province is not None:
            return self.province[self.province['region'].apply(lambda x: re.match(''.join(['^',province]), x) is not None)]
        else:
            return self.province[self.province['region'].apply(lambda x: re.match('^$', x) is not None)]

    def get_prefecture(self, province=None, prefecture=None):
        """ 获得地级行政区划

        :param str province: 省级行政区划
        :param str prefecture: 地级行政区划
        :return: 返回地级行政区划
        :rtype: pandas.DataFrame
        """
        prefecture_data = self.get_prefecture_children(province=province)
        if prefecture_data.size > 0:
            found = prefecture_data[prefecture_data['region'].apply(lambda x: re.match(prefecture, x) is not None)]
            if found.size > 0:
                return found
        return self.prefecture[self.prefecture['region'].apply(lambda x: re.match(prefecture, x) is not None)]

    def get_county(self, province=None, prefecture=None, county=None):
        counties = self.get_county_children(province=province,prefecture=prefecture)
        if counties.size > 0:
            county_found = counties[counties['region'].apply(lambda x: re.match(county, x) is not None)]
            if county_found.size > 0:
                return county_found

        return self.county[self.county['region'].apply(lambda x: re.match(county, x) is not None)]

    def region_table(self,year=None,province=True,prefecture=False,county=False):
        origin_year = self._year

        for i in range(len(year)):
            self._year = str(year[i])
            if i == 0:
                if province and (not prefecture) and (not county):
                    rtable = self.province.loc[:, ['acode', 'region']]
                elif province and prefecture and (not county):
                    rtable = self.province_and_prefecture.loc[:, ['acode', 'region']]
                elif province and (not prefecture) and county:
                    rtable = self.province_and_county.loc[:, ['acode', 'region']]
                elif province and prefecture and county:
                    rtable = self.all_region.loc[:, ['acode', 'region']]
                elif (not province) and prefecture and (not county):
                    rtable = self.prefecture.loc[:, ['acode', 'region']]
                elif (not province) and prefecture and county:
                    rtable = self.prefecture_and_county.loc[:, ['acode', 'region']]
                elif (not province) and (not prefecture) and county:
                    rtable = self.county.loc[:, ['acode', 'region']]

                rtable.columns.values[rtable.shape[1] - 1] = str(year[i])
            else:
                if province and (not prefecture) and (not county):
                    rtable = pd.merge(rtable, self.province.loc[:, ['acode', 'region']], how='outer', on='acode')
                elif province and prefecture and (not county):
                    rtable = pd.merge(rtable, self.province_and_prefecture.loc[:, ['acode', 'region']], how='outer', on='acode')
                elif province and (not prefecture) and county:
                    rtable = pd.merge(rtable, self.province_and_county.loc[:, ['acode', 'region']], how='outer', on='acode')
                elif province and prefecture and county:
                    rtable = pd.merge(rtable, self.all_region.loc[:, ['acode', 'region']], how='outer', on='acode')
                elif (not province) and prefecture and (not county):
                    rtable = pd.merge(rtable, self.prefecture.loc[:, ['acode', 'region']], how='outer', on='acode')
                elif (not province) and prefecture and county:
                    rtable = pd.merge(rtable, self.prefecture_and_county.loc[:, ['acode', 'region']], how='outer', on='acode')
                elif (not province) and (not prefecture) and county:
                    rtable = pd.merge(rtable, self.county.loc[:, ['acode', 'region']], how='outer', on='acode')

                rtable.columns.values[rtable.shape[1] - 1] = str(year[i])
        self._year = origin_year
        rtable = rtable.sort_values('acode')
        rtable.index = range(rtable.shape[0])
        return rtable

    def get_prefecture_children(self, province=None):
        found_acode = set(self.get_province(province=province)['acode'])
        if len(found_acode) == 1:
            found_acode = found_acode.pop()
            return self.prefecture[self.prefecture['acode'].apply(lambda x: re.match(''.join(['^', found_acode[0:2]]), x) is not None)]
        else:
            return self.get_province(province=province)

    def get_county_children(self, province=None, prefecture=None, county_type='all'):
        if prefecture is None:
            province_found = set(self.get_province(province=province)['acode'])
            if len(province_found) < 1:
                return self.get_province(province=province)
            elif len(province_found) < 2:
                found_acode = province_found.pop()
                all_county_children = self.county[self.county['acode'].apply(
                    lambda x: x[0:2] == found_acode[0:2])]

                if county_type == 'direct':
                    prefecture_children = set(self.get_prefecture_children(province=province)['acode'])
                    prefecture_code = set([prefecture[0:4] for prefecture in prefecture_children])
                    return self.county[self.county['acode'].apply(
                        lambda x: (x[0:2] == found_acode[0:2]) and (x[0:4] not in prefecture_code))]
                elif county_type == 'indirect':
                    prefecture_children = set(self.get_prefecture_children(province=province)['acode'])
                    prefecture_code = set([prefecture[0:4] for prefecture in prefecture_children])
                    return self.county[self.county['acode'].apply(
                        lambda x: x[0:4] in prefecture_code)]
                else:
                    return all_county_children
            else:
                print('More than two provinces provided!')
                raise Exception
        else:
            prefecture_found = set(self.get_prefecture(province=province, prefecture=prefecture)['acode'])
            if len(prefecture_found) < 1:
                return self.get_prefecture(province=province, prefecture=prefecture)
            elif len(prefecture_found) < 2:
                prefecture_code = prefecture_found.pop()
                return self.county[self.county['acode'].apply(
                    lambda x: x[0:4] == prefecture_code[0:4])]
            else:
                print('More than two prefectures provided!')
                raise Exception

    def get_prefecture_and_county_children(self, province=None):
        found_acode = set(self.get_province(province=province)['acode'])
        if len(found_acode) < 1:
            return self.get_province(province=province)
        elif len(found_acode) < 2:
            found_acode = found_acode.pop()
            return self.prefecture_and_county[self.prefecture_and_county['acode'].apply(
                lambda x: found_acode[0:2] == x[0:2])]
        else:
            print('More than one province provided!')
            raise Exception

    @property
    def province(self):
        province_list = list(self.database.find(adminlevel=2, year=self.year,
                                                projection={'_id':0,'region':1,'acode':1,'year':1,
                                                            'former':1,'uid':1,'parent':1, 'adminlevel':1},
                                                sorts=[('year',ASCENDING),('acode',ASCENDING)]))
        return pd.DataFrame(province_list,columns=['acode','region','year','uid', 'adminlevel', 'former','parent'])

    @property
    def prefecture(self):
        prefecture_list = list(self.database.find(adminlevel=3, year=self.year,
                                                  projection={'_id': 0, 'region': 1, 'acode': 1, 'year': 1,
                                                              'former': 1, 'uid': 1, 'parent': 1, 'adminlevel': 1},
                                                  sorts=[('year', ASCENDING), ('acode', ASCENDING)]))
        return pd.DataFrame(prefecture_list, columns=['acode', 'region', 'year', 'uid', 'adminlevel', 'former', 'parent'])

    @property
    def county(self):
        county_list = list(self.database.find(adminlevel=4, year=self.year,
                                              projection={'_id': 0, 'region': 1, 'acode': 1, 'year': 1,
                                                          'former': 1, 'uid': 1, 'parent': 1, 'grandpa': 1, 'adminlevel': 1},
                                              sorts=[('year', ASCENDING), ('acode', ASCENDING)]))
        return pd.DataFrame(county_list, columns=['acode', 'region', 'year', 'uid', 'adminlevel', 'former', 'parent','grandpa'])

    @property
    def province_and_prefecture(self):
        return self.all_region[self.all_region['adminlevel'].apply(lambda x: x == 2 or x == 3)]

    @property
    def province_and_county(self):
        return self.all_region[self.all_region['adminlevel'].apply(lambda x: x == 2 or x == 4)]

    @property
    def prefecture_and_county(self):
        return self.all_region[self.all_region['adminlevel'].apply(lambda x: x == 3 or x == 4)]

    @property
    def all_region(self):
        region_list = list(self.database.find(year=self.year,adminlevel=[2,3,4],
                                              projection={'_id': 0, 'region': 1, 'acode': 1, 'year': 1,
                                                          'former': 1, 'uid': 1, 'parent': 1, 'grandpa': 1,
                                                          'adminlevel': 1},
                                              sorts=[('year', ASCENDING), ('acode', ASCENDING)]))
        return pd.DataFrame(region_list,
                            columns=['acode', 'region', 'year', 'uid', 'adminlevel', 'former', 'parent', 'grandpa'])

    @property
    def year(self):
        return self._year

    @property
    def period(self):
        return sorted(list(self.database.collection.find().distinct('year')))

if __name__ == '__main__':
    adivision = AdminDivision(year=[2009])
    print(adivision.all_region)
    print(adivision.year)
    print(adivision.period)
    print(adivision.province)
    print(adivision.prefecture)
    print(adivision.county)
    #adivision.set_year('2008')
    print(adivision.get_prefecture_children(province='江苏'))
    prefecture_data = adivision.get_prefecture_children(province='江苏')
    print(prefecture_data[prefecture_data['region'].apply(lambda x: re.match('无锡', x) is not None)])
    print('-'*80)
    print(adivision.get_prefecture('江苏','苏州'))

    print(adivision.get_county_children(province='江苏',prefecture='苏州'))
    print(adivision.get_county_children(province='湖北',county_type='direct'))
    print(adivision.get_county(province='浙江',county='海宁'))
    print('-'*80)
    print(adivision['浙江'])
    print(adivision['浙江','杭州'])
    print(adivision['浙江','f'])
    print(adivision['浙江','嘉兴','海宁'])
    print(adivision['浙江','海宁'])
    print(adivision['江苏','昆山','f'])

    print('-'*80)
    print(adivision.region_table(year=range(1995,2005),prefecture=True))

    print('-'*80)
    print(adivision.get_prefecture_children())
    print(adivision.get_prefecture(province='安徽',prefecture='南京'))
    print(adivision.get_county_children(province='上海',prefecture='嘉兴'))
    print(adivision.get_county(province='上海',prefecture='嘉兴',county='海宁'))
    print(adivision.get_county(province='上海',prefecture='南京',county='昆山'))
    print(adivision.get_prefecture_and_county_children(province='江苏'))

    print('='*80)
    print(adivision['上海','南京','海宁'])
    print(adivision['吉林市'],type(adivision['吉林市']['region'].values[0]))
    print(adivision['浙江','海宁'])

    print('='*80)
    print(adivision.province_and_prefecture)