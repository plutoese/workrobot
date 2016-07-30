# coding = UTF-8

import random
import pandas as pd
from pandas.indexes.multi import MultiIndex
from libs.database.class_mongoceic import MonDBCEIC
from libs.utils.class_formatconverter import MongoDBToPandasFormat

# 0. Initialization
NUM_OF_VARIABLES = 2
YEARS = list(range(2000,2015))

# 1. 生成数据集
ceic_db = MonDBCEIC()
# 样本数据
sample_data = None
'''
# 1.2 查询
while True:
    random_vars = random.sample(ceic_db.variables,NUM_OF_VARIABLES)
    cursor = ceic_db.find({'variable':{'$in':random_vars},'year':{'$in': YEARS}},
                      projection={'_id':0,'variable':1,'value':1,'region':1,'acode':1,'year':1})
    ceid_raw_data = MongoDBToPandasFormat(cursor)
    result = ceid_raw_data(values='value', index=['acode','year'], columns='variable', dropna=True, balanced=True)
    if len(result) > 0:
        sample_data = result
        break

print(sample_data)
print(sample_data.index)
print(sample_data.index.ndim)
print(sample_data.index.labels[0])
print(isinstance(sample_data.index,MultiIndex))'''

class ToBe:
    def __init__(self):
        self.workflow = []
        self.rdata = [111,222,333]
        self._data = pd.DataFrame({'one' : pd.Series([1., 2., 3.], index=['a', 'b', 'c']),'two' : pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])})

    def add_workflow(self,object):
        self.workflow.append(object)

    def run(self):
        for item in self.workflow:
            result = item()

class NotToBe:
    def __init__(self, object):
        self.object = object

    def __call__(self, *args, **kwargs):
        self.object._data = self.object._data.pow(2)

tobe = ToBe()
nottobe = NotToBe(tobe)
tobe.add_workflow(nottobe)
tobe.run()
print(tobe._data)
print(tobe.rdata)