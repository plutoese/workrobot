# coding = UTF-8

# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# machine_five_ldmwp.py
# @简介：用python进行机器学习和数据挖掘
# @作者：Glen
# @日期：2016.8.16
# @资料来源：Python数据挖掘入门与实践
# +++++++++++++++++++++++++++++++++++++++++++++++++++++

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.feature_selection import VarianceThreshold
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.tree import DecisionTreeClassifier
from sklearn.cross_validation import cross_val_score
from sklearn.base import TransformerMixin
from sklearn.utils import as_float_array
from sklearn.pipeline import Pipeline

# ---------------------------------------
# 用转换器抽取特征
# ----------------------------------------

# 模型就是用来简化世界，特征抽取也是一样。
# 降低复杂性有好处，但也有不足，简化会忽略很多细节。

# 这里的例子用adult数据集，预测一个人是否年收入多于五万美元

# 1. 载入数据
adult_filename = r'E:\data\bigdata\adult\adult.data'
adult = pd.read_csv(adult_filename, header=None, names=["Age", "Work-Class", "fnlwgt", "Education",
                                                        "Education-Num", "Marital-Status", "Occupation",
                                                        "Relationship", "Race", "Sex", "Capital-gain",
                                                        "Capital-loss", "Hours-per-week", "Native-Country",
                                                        "Earnings-Raw"])

# 2. 数据清理
# 删除缺失数据
adult.dropna(how='all', inplace=True)

# 3. 探索性数据分析
# 描述统计
print(adult["Hours-per-week"].describe())

print(adult["Work-Class"].unique())

# 3'. 演示scikit-learn特征选择的方式
X = np.arange(30).reshape((10, 3))
X[:,1] = 1
# 注意：这时X矩阵中第二列全为1

# 利用VarianceThreshold()来删除方差低于阈值的变量
vt = VarianceThreshold()
Xt = vt.fit_transform(X)
# 这个时候，第二列就被删除了，因为它的方差为零
print(vt.variances_)

# 回到adult的例子，选择最佳特征
X = adult[["Age", "Education-Num", "Capital-gain", "Capital-loss", "Hours-per-week"]].values
y = (adult["Earnings-Raw"] == ' >50K').values

# 构建选择器
transformer = SelectKBest(score_func=chi2, k=3)
Xt_chi2 = transformer.fit_transform(X, y)

# 结论：相关性最好的分别是第一、三、四列
print(transformer.scores_)

# 还可以利用皮尔逊(Pearson)相关系数进行选择
# 这里利用了SciPy库的pearsonr()函数

# 定义函数
def multivariate_pearsonr(X, y):
    scores, pvalues = [], []
    for column in range(X.shape[1]):
        cur_score, cur_p = pearsonr(X[:,column], y)
        scores.append(abs(cur_score))
        pvalues.append(cur_p)
    return (np.array(scores), np.array(pvalues))

transformer = SelectKBest(score_func=multivariate_pearsonr, k=3)
Xt_pearson = transformer.fit_transform(X, y)
print(transformer.scores_)

# 利用CART分类器，查看特征选择的准确率
clf = DecisionTreeClassifier(random_state=14)
scores_chi2 = cross_val_score(clf, Xt_chi2, y, scoring='accuracy')
scores_pearson = cross_val_score(clf, Xt_pearson, y, scoring='accuracy')

print("Chi2 performance: {0:.3f}".format(scores_chi2.mean()))
print("Pearson performance: {0:.3f}".format(scores_pearson.mean()))

# 创建自己的转换器
# 转换器的API很简单。它接受一种特定格式的数据，输出一种格式的数据。

# 转换器有两个关键函数
# - fit(): 接受训练数据，设置内部参数
# - transform(): 转换过程。接受训练数据集或相同格式的新数据集。

# 转换器范例
class MeanDiscrete(TransformerMixin):
    def fit(self, X, y=None):
        X = as_float_array(X)
        self.mean = np.mean(X, axis=0)
        return self

    def transform(self, X):
        X = as_float_array(X)
        assert X.shape[1] == self.mean.shape[0]
        return X > self.mean

pipeline = Pipeline([('mean_discrete', MeanDiscrete()),
                     ('classifier', DecisionTreeClassifier(random_state=14))])
scores_mean_discrete = cross_val_score(pipeline, X, y, scoring='accuracy')
print("Mean Discrete performance: {0:.3f}".format(scores_mean_discrete.mean()))


