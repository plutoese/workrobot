# coding=UTF-8

import re
from dbadmin.popcensus.class_popcensusdatabase import PopCensusDatabase
from libs.datasheet.class_DataSheet import DataSheet
from libs.imexport.class_Excel import Excel

'''
# Appendix 1. to generate variable and unit mapping table
pop_census = PopCensusDatabase()

var_unit_mapping = []
for var in pop_census.variables:
    found = pop_census.collection._collection.find_one({'variable':var})
    if found is None:
        print('Not found!')
        raise Exception
    else:
        var_unit_mapping.append([var,found['unit']])

outfile = r'E:\data\popcensus\origin\var_unit_mapping.xlsx'
moutexcel = Excel(outfile)
moutexcel.new().append(var_unit_mapping, 'mysheet')
moutexcel.close()'''

# Appendix 2. to generate region and acode mapping table
# 1. year of 2010
pop_year = '2010'
pop_region_file_2010 = r'E:\data\popcensus\origin\var_temp.xls'
raw_region_2010 = Excel(pop_region_file_2010).read()

process_region_2010 = [re.sub('\s+','',item[0]) for item in raw_region_2010 if re.match('^\s*$',item[0]) is None]

# dirty work: correction for regions
process_region_2010 = [re.sub(u'巿',u'市',item) for item in process_region_2010]

if u'内邱县' in process_region_2010:
    process_region_2010[process_region_2010.index(u'内邱县')] = u'内丘县'
# 2010年2月22日，民政部下发了“关于吉林省白山市八道江区更名为浑江区的批复”（民函【2010】40号），
# 经国务院批准，吉林省白山市八道江区更名为浑江区。
if u'浑江区' in process_region_2010:
    process_region_2010[process_region_2010.index(u'浑江区')] = u'八道江区'
if u'狮河区' in process_region_2010:
    process_region_2010[process_region_2010.index(u'狮河区')] = u'浉河区'
if u'汩罗市' in process_region_2010:
    process_region_2010[process_region_2010.index(u'汩罗市')] = u'汨罗市'
if u'荔浦县' in process_region_2010:
    process_region_2010[process_region_2010.index(u'荔浦县')] = u'荔蒲县'
if u'江州区' in process_region_2010:
    process_region_2010[process_region_2010.index(u'江州区')] = u'江洲区'
if u'吴旗县' in process_region_2010:
    process_region_2010[process_region_2010.index(u'吴旗县')] = u'吴起县'

print(DataSheet.match_for_regions(process_region_2010,pop_year))