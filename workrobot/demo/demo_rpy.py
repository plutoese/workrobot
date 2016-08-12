# coding = UTF-8

import rpy2
from rpy2 import robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import IntVector, FloatVector, Formula, numpy2ri, Vector, Matrix, DataFrame
import numpy as np


# 版本号
print(rpy2.__version__)

# 导入R Package
base = importr('base')
print(dir(base))
print(base.pi)

# 获得R中的变量，调用__getitem__()方法
pi = robjects.r['pi']
print(pi, type(pi), len(pi), pi[0], pi.r_repr(), type(pi.r_repr()), float(pi.r_repr()))

# R的向量表达
res = robjects.StrVector(['abc', 'def'])

# R的函数，调用的参数如果是vector，dataframe或matrix，必须进行转换
#rsort = robjects.r['sort']
rsort = importr('base').sort
# Wrong：rsort([3,2,4])
print(rsort(IntVector([3,2,4])), type(rsort(IntVector([3,2,4]))))
# 调用函数时，记得R中用.的分隔符，在Python中用_替代
print(base.rank(0, na_last = True))

# 一个OLS的例子
# 构建R环境变量
stats = importr('stats')
# 可以查看R函数的参数列表
print(tuple(stats.rnorm.formals().names))

# 创建R形式的变量
ctl = FloatVector([4.17,5.58,5.18,6.11,4.50,4.61,5.17,4.53,5.33,5.14])
trt = FloatVector([4.81,4.17,4.41,3.59,5.87,3.83,6.03,4.89,4.32,4.69])

# 调用R下的gl函数
group = base.gl(2, 10, 20, labels = ["Ctl","Trt"])
# 注意，函数返回的也是R对象，这里group的类型是 <class 'rpy2.robjects.vectors.FactorVector'>
weight = ctl + trt

# 在R中创建全局变量
robjects.globalenv["weight"] = weight
robjects.globalenv["group"] = group
# 查看R中的全局变量
print('Variables in R enviroment: ', robjects.r.ls(robjects.globalenv))
# 列出base下提供的变量
print([x for x in robjects.r.baseenv()])

# 在Python中执行R函数
# 注意此时在R中已经有weight和group两个变量
lm_D9 = stats.lm("weight ~ group")

#print(stats.anova(lm_D9), type(stats.anova(lm_D9)))

# 每个R对象都有name属性
print('I am here', type(lm_D9), isinstance(lm_D9, Matrix), isinstance(lm_D9, DataFrame))
#print(lm_D9.names, type(lm_D9.names))
for item in lm_D9.names:
    print(item, type(lm_D9[lm_D9.names.index(item)]))
print(type(lm_D9[-2]),lm_D9[-2])
print('****************************')


# 解析R对象
print(lm_D9.rx('coefficients'), type(lm_D9.rx('coefficients')))
print(lm_D9.rx2('coefficients'), type(lm_D9.rx2('coefficients')))
print(lm_D9[0], type(lm_D9[0]),list(lm_D9[0].names))
print(lm_D9.rx2('call'))
print(type(lm_D9.rx2('call')), len(list(lm_D9.rx2('call').names)), len(np.array(lm_D9.rx2('call'))))
lm_D9_call = lm_D9.rx2('call')
for item in lm_D9_call:
    print('&&&&&&&&&&&&&&&&&&&&&&&')
    print(item)
    print('~~~~~~~~~~~~~~~~~~~~~~~')

print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
print(lm_D9.names)
for i in range(len(lm_D9)):
    item = lm_D9[i]
    if 'names' in dir(item):
        print(i, lm_D9.names[i], type(item), len(item), item.names)


'''
# 这里使用Formula形式
# 这里的weight ~ group是表达式
fmla = Formula('weight ~ group')
print(type(fmla.__repr__()))

# 使用OLS
fit1 = stats.lm(fmla)
print(fit1.names)
# 或者使用另一种方式
fit2 = robjects.r('lm(%s)' %fmla.r_repr())
print(tuple(fit2.names))

# 现在讨论vector
# 首先是StrVector
str_vec = robjects.StrVector('abc')
print(str_vec[0])
print('type: ', isinstance(str_vec,Vector))
# 可以转换为FactorVector
fac = robjects.FactorVector(str_vec)
print(fac.levels)

# 解析向量元素
x = robjects.r.seq(1,3)
x.names = robjects.StrVector(['a','b','c'])
print(x)

# ListVector是有名字的Vector
x = robjects.ListVector({'a': 1, 'b': 2, 'c': 3})
print(x.names)
print(x[x.names.index('b')])
x[x.names.index('b')] = 10
print(type(x))

# 讨论DataFrame
# 创建DataFrame
d = {'a': robjects.IntVector((1,2,3)), 'b': robjects.IntVector((4,5,6))}
dataf = robjects.DataFrame(d)
print(dataf, type(dataf), dataf.colnames, dataf.rownames)
# 查看列的type
print([column.rclass[0] for column in dataf])

# R和Python对象转换
# R对象转换为Python对象
r_vec = robjects.IntVector((1,2,3))
print(np.array(r_vec), type(np.array(r_vec)))

numpy2ri.activate()
x = np.array([1,2,3])
d2 = {'a': np.array([1,2,3]), 'b': np.array([4.2,2.4,3.6])}
dataf2 = robjects.DataFrame(d2)
print(dataf2, type(dataf2))

numpy2ri.deactivate()'''
