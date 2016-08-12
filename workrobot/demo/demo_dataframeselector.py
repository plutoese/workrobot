# coding = UTF-8

import pickle
import pandas as pd
import numpy as np
from collections import defaultdict

F = open(r'E:\github\workrobot\workrobot\files\ceic_raw_data_year.pkl', 'rb')
raw_data = pickle.load(F)

# 转换了index的数据
transformed_label_data = raw_data.swaplevel()

acodes = raw_data.index.get_level_values('acode').unique()
years = raw_data.index.get_level_values('year').unique()
variables = raw_data.columns

#print(raw_data)

select = (2010,['人口数','人口数_普查'])
select[1].append('互联网宽帶接入用户')
print(select)
rdata = raw_data.loc[select]
print(rdata)

#print(raw_data.index.get_level_values('acode').unique())
#print(transformed_label_data)

'''
# 数据集序列值
DATASET_MIN_NUMBER = 15

# 待记录的数据集
time_series_dataset = defaultdict()


# 目标1：时间序列数据
for acode in acodes[0:1]:
    enough_data_keys = set()
    enough_data_variables = set()
    single_variable_dataframe = dict()
    for variable in variables:
        dict_key = frozenset({acode, variable})
        mdata = pd.DataFrame(raw_data.loc[acode][variable].dropna())
        #print(time_series_dataset[dict_key].name, dict_key, len(time_series_dataset[dict_key]))
        if len(mdata) >= DATASET_MIN_NUMBER:
            time_series_dataset[dict_key] = mdata
            enough_data_keys.add(dict_key)
            enough_data_variables.add(variable)
            single_variable_dataframe[variable] = mdata

    print(len(enough_data_keys))
    for i in range(len(enough_data_variables)-1):
        print(i)
        if len(enough_data_keys) < 1:
            break
        more_enough_data_keys = set()
        for var in sorted(enough_data_variables):
            for d_key in sorted(enough_data_keys):
                print(i,'-',var,': ',d_key)
                if var in d_key:
                    continue
                merge_data = time_series_dataset[d_key].join(single_variable_dataframe[var]).dropna()
                if len(merge_data) >= (i+1)*DATASET_MIN_NUMBER:
                    d_key = d_key.union({var})
                    more_enough_data_keys.add(d_key)
                    time_series_dataset[d_key] = merge_data
        enough_data_keys = more_enough_data_keys


print(len(time_series_dataset))
print(time_series_dataset.keys())

for item in sorted((time_series_dataset.keys())):
    print(sorted(item),len(time_series_dataset[item]))'''






'''

new_data_1 = raw_data
new_data_1.index = raw_data.index.swaplevel()

new_data_2 = raw_data.swaplevel()
print(raw_data.index.tolist())
#print(raw_data.loc[raw_data.index.tolist()[0]])
#print(raw_data.loc[2004])

#print(new_data_1.index.tolist())
#print(new_data_2.index.tolist())

index_raw = raw_data.index.tolist()
index_new = [(item[1],item[0]) for item in new_data_2.index.tolist()]
#print(index_new)

print('\n***********************************\n')
for index_compare in index_raw:
    comparison = raw_data.loc[index_compare].equals(new_data_2.loc[(index_compare[1],index_compare[0])])

    if not comparison:
        print('NNNNNNNNNNNNNNNNNNNNNNNN')
print('Done')

'''

