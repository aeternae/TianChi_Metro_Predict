# TianChi_Metro_Predict

### 赛题简介

大赛开放了杭州20190101至20190125共25天地铁刷卡数据记录，共涉及3条线路81个地铁站约7000万条数据作为训练数据（Metro_train.zip），供选手搭建地铁站点乘客流量预测模型。训练数据（Metro_train.zip）解压后可以得到25个csv文件，每天的刷卡数据均单独存在一个csv文件中，以record为前缀。如2019年1月1日的所有线路所有站点的刷卡数据记录存储在record_2019-01-01.csv文件中，以此类推。同时大赛提供了路网地图，即各地铁站之间的连接关系表，存储在文件Metro_roadMap.csv文件中供选手使用。
[全球城市AI挑战赛](https://tianchi.aliyun.com/competition/entrance/231708/introduction)
![](pic/data.png)

### 思路

- 规则
  * 简单规则：用上一天的数据替代
  * 一般规则：对时间偏移多个固定量，求平均值，相对于简单规则可以提升0.5-0.8 mae
  * 稍复杂规则：将流量看成一种信号，进行滤波。经过线下测试，一阶滞后滤波效果较好，滞后因子取0.15-0.2。有兴趣的小伙伴可以尝试卡尔曼滤波，效果不知。
  * 强规则：前排规则大佬的规则，静待开源

- 模型
  * LSTM （想做没来得及做）

  * LGB （baselineB榜首次提交12.28，结果int后12.18）

    ![](https://raw.githubusercontent.com/BirderEric/Tianchi_CityAI_Challenge/master/code/Screen%20Shot%202019-04-05%20at%2010.17.33%20AM.png)

  * *StationID*不能作为连续值训练，应该将其作为类别特征，One-hot效果不及直接将其作为LGB的*category_feature='stationID'*效果来的好，大概好0.5mae
- 如何构建训练集
  * 取决于测试集的时间，预测周日那么就选取周日的数据作为训练集，因为周末与工作日的流量分布相差很大。如果是工作日，那么就剔除双休日，其余的数据都可以作为训练集。
  * 特征的选取，baseline选取了前面五天的历史时间段统计流量和上下一个时间段的流量作为特征。
- 调优
  * 模型参数调优(*max_depth* eta.)
  * 预测数据后处理，取整数，去负数，乘系数(系数可以根据前一天的进出站总流量/预测总流量近似求解）。
- baseline不足
  - 只包含inNums 和 outNums统计特征
  - 没有对高*mae*站台（杭州东站）建立特殊规则或模型
  - 没有利用提供的`roadMap`、`paytype`、`deviceID`细化特征


