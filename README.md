# CityAI Baseline Doc

### 赛题简介

![](http://aliyuntianchiresult.cn-hangzhou.oss.aliyun-inc.com/public/files/forum/1552965164939.png)

大赛以“地铁乘客流量预测”为赛题，参赛者可通过分析地铁站的历史刷卡数据，预测站点未来的客流量变化，帮助实现更合理的出行路线选择，规避交通堵塞，提前部署站点安保措施等，最终实现用大数据和人工智能等技术助力未来城市安全出行。

大赛开放了20190101至20190125共25天地铁刷卡数据记录，共涉及3条线路81个地铁站约7000万条数据作为训练数据（Metro_train.zip），供选手搭建地铁站点乘客流量预测模型。训练数据（Metro_train.zip）解压后可以得到25个csv文件，每天的刷卡数据均单独存在一个csv文件中，以record为前缀。如2019年1月1日的所有线路所有站点的刷卡数据记录存储在record_2019-01-01.csv文件中，以此类推。同时大赛提供了路网地图，即各地铁站之间的连接关系表，存储在文件Metro_roadMap.csv文件中供选手使用。

测试阶段，大赛将提供某天所有线路所有站点的刷卡数据记录，选手需预测未来一天00时至24时以10分钟为单位各时段各站点的进站和出站人次。

预选赛阶段，测试集A集上，大赛将提供2019年1月28日的刷卡数据（testA_record_2019-01-28.csv），选手需对2019年1月29日全天各地铁站以10分钟为单位的人流量进行预测，淘汰赛和决赛将分别更新一批新的数据测试集B集和测试集C集。

[全球城市AI挑战赛](https://tianchi.aliyun.com/competition/entrance/231708/introduction)

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

### 函数

```python
load_file(daystart:int,dayend:int)
    #加载数据集
  	'''
  	@param int daystart:加载开始日期
    @param int dayend:加载终止日期
  	'''
    
time_pro(sheet:pd.DataFrame)
		#数据集数据时间预处理，提取出month、day、hour、min 	
    '''
    @param pd.DataFrame sheet
    :return pd.DataFrame sheet
    '''

perSt_perDay_perTen_count(df)
		#统计每个站台每天每10分钟的进出流量情况
  	'''
  	@param pd.DataFrame sheet
    :return pd.DataFrame sheet
  	'''

time_clip(df)
		#设计之初是来对时间进行偏移，clip=1,即表示原来0-10分钟转换为1-11分钟

findpeak(array:np.array)

		#记录站台一天中流量的尖峰值，返回索引

findvalley(array:np.array)
		#记录站台一天中流量的谷值，返回索引

day_res_extract(df)
		#提取每天每个站台每分钟的流量结果

gen_train_data()
		#生成B榜训练集
  	#B榜预测的为27日，故训练集中的历史数据选取前5天的历史数据作为特征
    #历史数据指的是在相同的时间段历史的流量统计

shift()
		#提取前一个和后一个时间段的站台流量特征

load_train_file()
		#加载数据集，并且时间预处理

load_train_valid()
		#生成训练集数据与验证集数据
    #B榜把6、13、20的数据作为训练集标签，并且对这三天构造训练数据及特征

train()
		#模型训练，选用LGB模型，5折交叉验证

gen_submit()
		#生成提交文件

```



### 吐槽

从交流群了解到，c榜的成绩同样发生了很大变化，第2，3，4，6名全部跌出决赛圈，真的挺可惜，那我要吐槽的是官方居然以`避免不必要的麻烦、需要内部协调后在答辩前公布成绩`迟迟没有放出榜单，可想而知以上四支队伍的心情。自己也参加过不少比赛，虽然对主办方可能都会有这样或那样的抱怨，但是至少成绩是公开的，比赛我觉得应该多像Kaggle学习，在赛制和评分方面我不反对设置*abcdef*榜，但是不希望以现在这样的形式，要让每个人都能参与，要让每个人都能获得这*abcdef*榜的成绩作为自己过去付出的反馈，评价一个模型的好坏不应该像摸奖一样充满刺激。



