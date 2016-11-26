# coding=UTF-8

# -----------------------------------------------------------------------------------------
# @author: plutoese
# @date: 2015.10.10
# @class: AdminData
# @introduction: 类AdminData表示数据，是超类，用来被继承。
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
# -----------------------------------------------------------------------------------------

import re
from dbadmin.admincode.class_admindatabase import AdminDatabase
from dbadmin.admincode.class_data import Data
from pymongo import ASCENDING


class AdminData:
    """ 类AdminData表示行政区划数据

    """

    # 构造函数
    def __init__(self,version=None,year=None):
        Data.__init__(self)
        # 设置数据库
        self.database = AdminDatabase()

        # 设置最新版本
        self.latestversion = self.database.version()[len(self.database.version())-1]

        # 设置版本和年份
        if (version is None) and (year is None):
            self.version = self.latestversion
            self.year = re.split('_',self.version)[0]
        elif version is not None:
            self.version = version
            self.year = re.split('_',self.version)[0]
        else:
            self.year = str(year)
            self.version = self.database.version(self.year)[len(self.database.version(self.year))-1]

    # to get item
    # f to get all first level
    # s to get all second level
    # b to get all first and second level
    def __getitem__(self, key):
        if isinstance(key,str):
            if re.match('^s$',key):
                return self.Province
            if re.match('^t$',key):
                return self.Prefecture
            if re.match('^f$',key):
                return self.County
            return self._getProvince(key)
        if isinstance(key,tuple) and len(key) < 2:
            if re.match('^s$',key[0]):
                return self.Province
            if re.match('^t$',key[0]):
                return self.Prefecture
            if re.match('^f$',key[0]):
                return self.County
            return self._getProvince(key[0])
        if isinstance(key,tuple):
            if len(key) < 3:
                if re.match(key[1],u'f') is not None:
                    result = self._getPrefectureChildren(key[0])
                    if result is None:
                        return None
                    return self._sorted(result)
                elif re.match(key[1],u's') is not None:
                    prefectures = self._getPrefectureChildren(key[0])
                    if prefectures is None:
                        return None
                    result = []
                    for item in prefectures:
                        result.extend(self._getCountyChildren(key[0],item['region']))
                    return self._sorted(result)
                elif re.match(key[1],u'b') is not None:
                    prefectures = self._getPrefectureChildren(key[0])
                    if prefectures is None:
                        return None
                    result = []
                    for item in prefectures:
                        result.append(item)
                        result.extend(self._getCountyChildren(key[0],item['region']))
                    return self._sorted(result)
                else:
                    result = self._getPrefecture(key[0],key[1])
                    if result is None:
                        result = self._getCounty(province=key[0],county=key[1])
                        return result
                    else:
                        return result
            else:
                if re.match(key[2],u'f') is not None:
                    result = self._getCountyChildren(key[0],key[1])
                    if result is None:
                        return None
                    return self._sorted(result)
                else:
                    result = self._getCounty(key[0],key[1],key[2])
                    return result

    # 通过Acode获得区域
    def getByAcode(self,acode,year=None):
        if year is None:
            return list(self.database.find(acode=acode,version=self.version))
        else:
            version = self.database.version(year)[len(self.database.version(str(year)))-1]
            return list(self.database.find(acode=acode,version=version))

    # 获得一个省级单位
    # 这里可以不是精确匹配
    def _getProvince(self,province):
        _provincepattern = u'省|市|自治区|维吾尔自治区|回族自治区|壮族自治区'
        province = re.split(_provincepattern,re.sub('\s+','',province))[0]
        mprovince = '^' + province +'$'
        result = [item for item in self.Province if re.match(mprovince,re.split(_provincepattern,item['region'])[0]) is not None]
        if len(result) < 1:
            return None
        return result

    # 获得一个地级单位
    def _getPrefecture(self,province,prefecture):
        prefectures =  self._getPrefectureChildren(province)
        result = [item for item in prefectures if re.match(prefecture,item['region']) is not None]
        if len(result) < 1:
            return None
        return result

    # 获得一个县级单位
    def _getCounty(self,province,prefecture=None,county=None):
        counties =  self._getCountyChildren(province,prefecture)
        if counties is None:
            return None
        result = [item for item in counties if re.match(county,item['region']) is not None]
        if len(result) < 1:
            return None
        return result

    # 获得一个省级单位所有的地级单位
    def _getPrefectureChildren(self,province):
        # to find province item
        provinces = self._getProvince(province)
        if provinces is None:
            print(u'找不到这个省份: ',province)
            return None
        if len(provinces) > 1:
            return None
        prefecture = self.database.find(parent=provinces[0]['_id'],version=self.version,sorts=[('acode',ASCENDING)])
        return list(prefecture)

    # 获得一个地级单位所有的县级单位
    def _getCountyChildren(self,province,prefecture=None):
        # to find province item
        if prefecture is not None:
            prefectures = self._getPrefecture(province,prefecture)
            if prefectures is None:
                #print(u'找不到这个地级市: ',prefecture)
                return None
            if len(prefectures) > 1:
                return None
            county = self.database.find(parent=prefectures[0]['_id'],version=self.version,sorts=[('acode',ASCENDING)])
            return list(county)
        else:
            province_code = self._getProvince(province)[0].get('acode')
            return [item for item in self.County if re.match(''.join(['^',province_code[0:2],'\d{4}$']),item.get('acode')) is not None]

    # 设置版本
    def setVersion(self,version):
        self.version = version
        self.year = re.split('_',self.version)[0]

    # 设置年份
    def setYear(self,year):
        self.year = str(year)
        self.version = self.database.version(self.year)[len(self.database.version(self.year))-1]

    # 所有的省级单位
    @property
    def Province(self):
        return self._sorted(list(self.database.find(adminlevel=2,version=self.version)))

    # 所有的省级单位
    @property
    def Prefecture(self):
        return self._sorted(list(self.database.find(adminlevel=3,version=self.version)))

    # 所有的省级单位
    @property
    def County(self):
        return self._sorted(list(self.database.find(adminlevel=4,version=self.version)))

    # 获得省级和地级单位
    @property
    def ProvincePrefecture(self):
        result = []
        provinces = self.Province
        for province in provinces:
            result.append(province)
            result.extend(self._getPrefectureChildren(province['region']))
        return result

    # 获得省级、地级和县级单位
    @property
    def ProvincePrefectureCounty(self):
        result = []
        provinces = self.Province
        for province in provinces:
            result.append(province)
            prefectures = self._getPrefectureChildren(province['region'])
            for prefecture in prefectures:
                result.append(prefecture)
                result.extend(self._getCountyChildren(province['region'],prefecture['region']))
        return result

    # 辅助排序函数
    def _sorted(self,regions):
        return sorted(regions,key = lambda x:x['acode'])


if __name__ == '__main__':
    adata = AdminData(year=2004)
    print(adata.version)
    print(adata.Province)
    print(adata._getProvince(u'浙江'))
    print(adata._getPrefectureChildren(u'浙江'))
    print(adata._getPrefecture(province=u'浙江',prefecture=u'嘉兴市'))
    print(adata._getCountyChildren(province=u'浙江',prefecture=u'嘉兴市'))
    print(adata._getCounty(province=u'浙江',prefecture=u'嘉兴市',county=u'平湖市'))
    print(adata.getByAcode('220000'))
    print(adata.ProvincePrefecture)

    print(adata[u'浙江','b'])
    print(adata[u'浙江',u'嘉兴',u'孩孩'])
    provinces = {item['acode']:item['region'] for item in adata.Province}
    print(provinces)

    adata.setYear(2010)
    print(adata[tuple([u'浙江',u'f'])])
    print(adata[tuple([u'新疆'])])
    print(adata[tuple([u'吉林省',u'九台市'])])


















