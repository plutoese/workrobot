# coding=UTF-8

from library.datapretreatment.class_DataSheet import *
from library.region.AdminCode.class_AdministrativeCode import *

# 类CityStatisticsDataSheet用来处理中国城市统计年鉴的数据
class CityStatisticsDataSheet(DataSheet):
    '''
    类CityStatisticsDataSheet用来处理中国城市统计年鉴的数据
    
    属性：
    self.rawdata: 原始数据
    '''
    # 构造函数
    def __init__(self, filename=None,sheetnum=0,year=None):
        DataSheet.__init__(self,filename=filename,sheetnum=sheetnum)
        self._data = pd.DataFrame(self.rawdata)
        self.year = year
        self.wrongnumber = []

        # 设置ad选项
        self.ad = AdministrativeCode(year=year)

        # 设置表头
        for item in self.rawdata:
            if re.match('^\s*$',item[0]) is None:
                print('表格名字:',item[0])
                self.title = item[0]
                break

        self.rowdatastart = 2

    # 导入变量和单位
    def setVariables(self,varlist):
        self.vars = [re.split(':',item) for item in varlist if re.match('^\s*$',item) is None]
        self.nvars = len(self.vars)

    # 组合数据
    def _toDicts(self,region,ldata):
        result = []
        for i in range(self.nvars):
            value = re.sub('\s+','',str(ldata[i]))
            if re.match('^[-]?\d+(\.\d+)?$',value) is not None:
                record = {'source':u'中国城市统计年鉴','tableTitle':self.title,'year':self.year,'region':region['region'],'acode':region['acode'],'regionid':region['_id'],'variable':self.vars[i][0],'scale':self.vars[i][1],'unit':self.vars[i][2],'value':float(value)}
                result.append(record)
            else:
                if len(value) > 0:
                    self.wrongnumber.append([self.title,region['region'],self.vars[i][0],value])
                print('Wrong with number',ldata[i])
        return result

    # 析出数据表格
    def todataTable(self):
        mdata = self.data
        result = []
        prefix = []
        self.wrongdata = []
        self.region = []
        for i in mdata.index:
            if len(re.sub('\s+','',mdata.iloc[i][0])) < 1:
                print('Wrong region',mdata.iloc[i][0])
                self.wrongdata.append(mdata.iloc[i][0])
                continue
            if re.search('\(|\)',mdata.iloc[i][0]) is not None:
                print('Wrong region',mdata.iloc[i][0])
                self.wrongdata.append(mdata.iloc[i][0])
                continue

            # 设置一些特别的容易出错的地区
            if self.year == 2010:
                if re.match(u'^襄阳市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                    mdata.iloc[i][0] = u'襄樊市'

            if self.year == 2009:
                if re.match(u'^襄阳市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                    mdata.iloc[i][0] = u'襄樊市'
                if re.match(u'^思茅市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                    mdata.iloc[i][0] = u'普洱市'

            if self.year == 2008:
                if re.match(u'^思茅市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                    mdata.iloc[i][0] = u'普洱市'

            if self.year == 2007:
                if re.match(u'^思茅市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                    mdata.iloc[i][0] = u'普洱市'

            if self.year == 2006:
                if re.match(u'^恩茅市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                    mdata.iloc[i][0] = u'思茅市'
                if re.match(u'^普洱市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                    mdata.iloc[i][0] = u'思茅市'

            if self.year == 2003:
                if re.match(u'^海拉尔$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                    mdata.iloc[i][0] = u'呼伦贝尔市'

            if self.year == 2002:
                if re.match(u'^海拉尔$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                    mdata.iloc[i][0] = u'呼伦贝尔市'

            if re.match(u'^准安市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'淮安市'
            if re.match(u'^准北市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'淮北市'
            if re.match(u'^准南市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'淮南市'
            if re.match(u'^台帅市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'台州市'
            if re.match(u'^衙州市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'衢州市'
            if re.match(u'^同原市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'固原市'
            if re.match(u'^宜城市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'宣城市'
            if re.match(u'^青安市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'吉安市'
            if re.match(u'^平顺山市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'平顶山市'
            if re.match(u'^胡南省$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'湖南省'
            if re.match(u'^毫州|毫州市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'亳州市'
            if re.match(u'^褊州市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'福州市'
            if re.match(u'^来寅市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'来宾市'
            if re.match(u'^胡芦岛市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'葫芦岛市'
            if re.match(u'^攀枝化市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'攀枝花市'
            if re.match(u'^洒泉市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'酒泉市'
            if re.match(u'^长冶市$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'长治市'
            if re.match(u'^成宁$',re.sub('\s+','',mdata.iloc[i][0])) is not None:
                mdata.iloc[i][0] = u'咸宁'

            if len(prefix) < 1:
                region = self.ad[re.sub('\s+','',mdata.iloc[i][0])]
                if region is None:
                    print('Wrong0:',mdata.iloc[i][0])
                    self.wrongdata.append(mdata.iloc[i][0])
                else:
                    result.extend(self._toDicts(region,list(mdata.iloc[i][self.rowdatastart:])))
                    prefix.append(region['region'])
            elif len(prefix) < 2:
                region = self.ad[re.sub('\s+','',mdata.iloc[i][0])]
                if region is None:
                    region = self.ad[prefix[0],re.sub('\s+','',mdata.iloc[i][0])]
                    if region is None:
                        print('Wrong1:',mdata.iloc[i][0])
                        self.wrongdata.append(mdata.iloc[i][0])
                    else:
                        result.extend(self._toDicts(region,list(mdata.iloc[i][self.rowdatastart:])))
                        prefix.append(region['region'])
                else:
                    if re.match(self.ad[prefix[len(prefix)-1]]['acode'],region['acode']) is not None:
                        region = self.ad[prefix[0],re.sub('\s+','',mdata.iloc[i][0])]
                        if region is None:
                            print('Wrong1:',mdata.iloc[i][0])
                            self.wrongdata.append(mdata.iloc[i][0])
                        else:
                            result.extend(self._toDicts(region,list(mdata.iloc[i][self.rowdatastart:])))
                            prefix.append(region['region'])
                    else:
                        result.extend(self._toDicts(region,list(mdata.iloc[i][self.rowdatastart:])))
                        prefix = [region['region']]
            else:
                region = self.ad[re.sub('\s+','',mdata.iloc[i][0])]
                if region is None:
                    region = self.ad[prefix[0],re.sub('\s+','',mdata.iloc[i][0])]
                    if region is None:
                        region = self.ad[prefix[0],prefix[1],re.sub('\s+','',mdata.iloc[i][0])]
                        if region is None:
                            print('Wrong2:',mdata.iloc[i][0])
                            self.wrongdata.append(mdata.iloc[i][0])
                        else:
                            result.extend(self._toDicts(region,list(mdata.iloc[i][self.rowdatastart:])))
                    else:
                        result.extend(self._toDicts(region,list(mdata.iloc[i][self.rowdatastart:])))
                        prefix[1] = region['region']
                else:
                    result.extend(self._toDicts(region,list(mdata.iloc[i][self.rowdatastart:])))
                    prefix = [region['region']]
            self.region.append(mdata.iloc[i][0])
        return result

if __name__ == '__main__':
    ad = AdministrativeCode(year=2012)
    mdatasheet = CityStatisticsDataSheet(r'C:\Data\city\data\m01.xlsx',year=2012)

    filename = r'C:\Data\city\var\m2012.xlsx'
    variables = Excel(filename).read(sheetnum=0)
    var = variables[0][1:]
    mdatasheet.setVariables(var)
    print(mdatasheet.nvars)

    result = mdatasheet.todataTable()
    print(result)






