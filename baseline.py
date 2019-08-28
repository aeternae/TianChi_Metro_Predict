import pandas as pd
import numpy as np
import gc
import matplotlib.pyplot as plt
import os

creatVars = locals()

test = pd.read_csv('../input/Metro_testA/testA_submit_2019-01-29.csv')
test_28 = pd.read_csv('../input/Metro_testA/testA_record_2019-01-28.csv')
def get_base_features(df_):
    
    df = df_.copy()
    
    # base time
    df['day']     = df['time'].apply(lambda x: int(x[8:10]))
    df['week']    = pd.to_datetime(df['time']).dt.dayofweek + 1
    df['weekend'] = (pd.to_datetime(df.time).dt.weekday >=5).astype(int)
    df['hour']    = df['time'].apply(lambda x: int(x[11:13]))
    df['minute']  = df['time'].apply(lambda x: int(x[14:15]+'0'))
    
    # count,sum
    result = df.groupby(['stationID','lineID', 'week', 'weekend', 'day', 'hour', 'minute']).status.agg(['count', 'sum']).reset_index()
    
    # nunique
    
    
    tmp     = df.groupby(['stationID'])['deviceID'].nunique().reset_index(name='nuni_deviceID_of_stationID')
    result  = result.merge(tmp, on=['stationID'], how='left')
    tmp     = df.groupby(['stationID','hour'])['deviceID'].nunique().reset_index(name='nuni_deviceID_of_stationID_hour')
    result  = result.merge(tmp, on=['stationID','hour'], how='left')
    tmp     = df.groupby(['stationID','hour','minute'])['deviceID'].nunique().\
                                           reset_index(name='nuni_deviceID_of_stationID_hour_minute')
    result  = result.merge(tmp, on=['stationID','hour','minute'], how='left')
    
    # in,out
    result['inNums']  = result['sum']
    result['outNums'] = result['count'] - result['sum']
    
    #
    result['day_since_first'] = result['day'] - 1 
    result.fillna(0, inplace=True)
    del result['sum'],result['count']
    
    return result

data = get_base_features(test_28)

data_list = os.listdir('../input/Metro_train/')
for i in range(0, len(data_list)):
    if data_list[i].split('.')[-1] == 'csv':
        print(data_list[i], i)
        df = pd.read_csv('../input/Metro_train/' + data_list[i])
        df = get_base_features(df)
        data = pd.concat([data, df], axis=0, ignore_index=True)
    else:
        continue

		
test = pd.merge(test,test_28[['stationID','lineID']].drop_duplicates(),on='stationID',how='left')	
		
def fix_day(d):
    if d in [1,2,3,4]:
        return d
    elif d in [7,8,9,10,11]:
        return d - 2
    elif d in [14,15,16,17,18]:
        return d - 4
    elif d in [21,22,23,24,25]:
        return d - 6
    elif d in [28]:
        return d - 8
    
def get_refer_day(d):
    if d == 20:
        return 29
    else:
        return d + 1    
def recover_day(d):
    if d in [1,2,3,4]:
        return d
    elif d in [5,6,7,8,9]:
        return d + 2
    elif d in [10,11,12,13,14]:
        return d + 4
    elif d in [15,16,17,18,19]:
        return d + 6
    elif d == 20:
        return d + 8
    else:
        return d    
    
    
    # 剔除周末,并修改为连续时间
data = data[(data.day!=5)&(data.day!=6)]
data = data[(data.day!=12)&(data.day!=13)]
data = data[(data.day!=19)&(data.day!=20)]
data = data[(data.day!=26)&(data.day!=27)]


data['day'] = data['day'].apply(fix_day)


test['week']    = pd.to_datetime(test['startTime']).dt.dayofweek + 1
test['weekend'] = (pd.to_datetime(test.startTime).dt.weekday >=5).astype(int)
test['day']     = test['startTime'].apply(lambda x: int(x[8:10]))
test['hour']    = test['startTime'].apply(lambda x: int(x[11:13]))
test['minute']  = test['startTime'].apply(lambda x: int(x[14:15]+'0'))
test['day_since_first'] = test['day'] - 1
test = test.drop(['startTime','endTime'], axis=1)
data = pd.concat([data,test], axis=0, ignore_index=True)

stat_columns = ['inNums','outNums']

tmp = data.copy()
tmp_df = tmp[tmp.day==1]
tmp_df['day'] = tmp_df['day'] - 1

tmp = pd.concat([tmp, tmp_df], axis=0, ignore_index=True)
tmp['day'] = tmp['day'].apply(get_refer_day)
for f in stat_columns:
    tmp.rename(columns={f: f+'_last'}, inplace=True) 

tmp = tmp[['stationID','day','hour','minute','inNums_last','outNums_last']]

data = data.merge(tmp, on=['stationID','day','hour','minute'], how='left')
data.fillna(0, inplace=True)

tmp = data.groupby(['stationID','week','hour','minute'], as_index=False)['inNums'].agg({
                                                                        'inNums_whm_max'    : 'max',
                                                                        'inNums_whm_min'    : 'min',
                                                                        'inNums_whm_mean'   : 'mean'
                                                                        })
data = data.merge(tmp, on=['stationID','week','hour','minute'], how='left')

tmp = data.groupby(['stationID','week','hour','minute'], as_index=False)['outNums'].agg({
                                                                        'outNums_whm_max'    : 'max',
                                                                        'outNums_whm_min'    : 'min',
                                                                        'outNums_whm_mean'   : 'mean'
                                                                        })
data = data.merge(tmp, on=['stationID','week','hour','minute'], how='left')

tmp = data.groupby(['stationID','week','hour'], as_index=False)['inNums'].agg({
                                                                        'inNums_wh_max'    : 'max',
                                                                        'inNums_wh_min'    : 'min',
                                                                        'inNums_wh_mean'   : 'mean'
                                                                        })
data = data.merge(tmp, on=['stationID','week','hour'], how='left')

tmp = data.groupby(['stationID','week','hour'], as_index=False)['outNums'].agg({
                                                                        #'outNums_wh_max'    : 'max',
                                                                        #'outNums_wh_min'    : 'min',
                                                                        'outNums_wh_mean'   : 'mean'
                                                                        })
data = data.merge(tmp, on=['stationID','week','hour'], how='left')


data_A = data[data['lineID']=='A']
data_B = data[data['lineID']=='B']
data_C = data[data['lineID']=='C']
test_A = test[test['lineID']=='A']
test_B = test[test['lineID']=='B']
test_C = test[test['lineID']=='C']
del data_A['lineID']
del data_B['lineID']
del data_C['lineID']
del test_A['lineID']
del test_B['lineID']
del test_C['lineID']
gc.collect()


import lightgbm as lgb
params = {
    'boosting_type': 'gbdt',
    'objective': 'regression',
    'metric': 'mae',
    'num_leaves': 63,
    'learning_rate': 0.01,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.9,
    'bagging_seed':0,
    'bagging_freq': 1,
    'verbose': 1,
    'reg_alpha':1,
    'reg_lambda':2
}


use_data = data_A/data_B/data_C

all_columns = [f for f in use_data.columns if f not in ['weekend','inNums','outNums']]
### all data
all_data = use_data[use_data.day!=29]
all_data['day'] = all_data['day'].apply(recover_day)
X_data = all_data[all_columns].values

train = use_data[use_data.day <20]
train['day'] = train['day'].apply(recover_day)
X_train = train[all_columns].values

valid = use_data[use_data.day==20]
valid['day'] = valid['day'].apply(recover_day)
X_valid = valid[all_columns].values

use_test  = use_data[use_data.day==29]
X_test = use_test[all_columns].values

######################################################inNums
y_train = train['inNums']
y_valid = valid['inNums']
y_data  = all_data['inNums']
lgb_train = lgb.Dataset(X_train, y_train)
lgb_evals = lgb.Dataset(X_valid, y_valid , reference=lgb_train)
gbm = lgb.train(params,
                lgb_train,
                num_boost_round=10000,
                valid_sets=[lgb_train,lgb_evals],
                valid_names=['train','valid'],
                early_stopping_rounds=200,
                verbose_eval=1000
                )
### all_data
lgb_train = lgb.Dataset(X_data, y_data)
gbm = lgb.train(params,
                lgb_train,
                num_boost_round=gbm.best_iteration,
                valid_sets=[lgb_train],
                valid_names=['train'],
                verbose_eval=1000
                )
use_test['inNums'] = gbm.predict(X_test)

y_train = train['outNums']
y_valid = valid['outNums']
y_data  = all_data['outNums']
lgb_train = lgb.Dataset(X_train, y_train)
lgb_evals = lgb.Dataset(X_valid, y_valid , reference=lgb_train)
gbm = lgb.train(params,
                lgb_train,
                num_boost_round=10000,
                valid_sets=[lgb_train,lgb_evals],
                valid_names=['train','valid'],
                early_stopping_rounds=200,
                verbose_eval=1000,
                )

### all_data
lgb_train = lgb.Dataset(X_data, y_data)
gbm = lgb.train(params,
                lgb_train,
                num_boost_round=gbm.best_iteration,
                valid_sets=[lgb_train],
                valid_names=['train'],
                verbose_eval=1000,
                )
use_test['outNums'] = gbm.predict(X_test)

test_A['inNums'] = use_test['inNums'].values
test_A['outNums'] = use_test['outNums'].values

test_B['inNums'] = use_test['inNums'].values
test_B['outNums'] = use_test['outNums'].values

test_C['inNums'] = use_test['inNums'].values
test_C['outNums'] = use_test['outNums'].values

del test['inNums']
del test['outNums']		
tteat = pd.concat([test_B,test_C])
tteat = pd.concat([tteat,test_A])	
		
tteat = pd.merge(test,tteat,how='left')
tteat.fillna(0,inplace=True)		
		
sub = pd.read_csv('../input/Metro_testA/testA_submit_2019-01-29.csv')
sub['inNums']   = tteat['inNums'].values
sub['outNums']  = tteat['outNums'].values
# 结果修正
sub.loc[sub.inNums<0 , 'inNums']  = 0
sub.loc[sub.outNums<0, 'outNums'] = 0
sub[['stationID', 'startTime', 'endTime', 'inNums', 'outNums']].to_csv('../output/sub_baseline_div_a_b_c.csv', index=False)		
		
		
		
		
		
		
		

