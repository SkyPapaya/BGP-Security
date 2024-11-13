# Feature Extraction
Feature extraction for machine learning.

# 代码介绍
> Data_generator.py

根据Updates消息生成固定时间窗口的样本；

> time_slice.py

根据样本计算统计类特征；

> Graph_feature.py, Graph_feature_foc.py

根据样本提取图相关特征；

> plot_attribute.py

对提取好的特征按照时间序列的方式进行可视化检验；

> Detect_anomaly.py

使用Simhash进行图结构的同构性检测；


# 实验过程
* 组建实验环境，现在数据代码以及解析代码，见bgpmagnet\、parse.sh
* 开发样本生成器，见```Data_generator.py```
* 开发统计特征的计算程序，见```time_slice.py  ```
* 开发基于图特征的提取代码，见```Graph_feature.py```、```Routes.py```
* 开发基于关注图特征的提取代码，见```Graph_feature_foc.py```
* 对提取的特征进行验证：对特征进行可视化，见```plot_attribute.py```; 转化为arff WEKA形式验证其准确率，见```t2arff.py```
* 2022-11-28 构建无监督的BGP异常检测代码，使用SimHash,见```Detect_anomaly.py```
* 2022-11-29 使用GNN算法进行异常检测，见```Gnn_test.py```
* 2022-12-15 使用```pyg```进行GCN实验