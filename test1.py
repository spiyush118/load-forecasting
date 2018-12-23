from numpy import concatenate
from numpy import roll
from matplotlib import pyplot as plt
import pandas as pd
from pandas import read_csv
from pandas import DataFrame
from pandas import concat,merge
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from data_utils import *
from get_data import *
from model import *
import os
import glob
import numpy as np


##Data=DataFrame()

s_load,s_weather=file_list()
update_weather(list(s_weather.keys())[-1][-14:-4])
update_load(list(s_load.keys())[-1][-14:-4])
forecast_weather()

##s_load=collections.OrderedDict.fromkeys([])
##s_weather=collections.OrderedDict.fromkeys([])
Data=pd.read_csv('final_data1.csv')
data,f_data=final_data(Data,s_load,s_weather)
n_features=5
time_step=5
n_out=1
batch_size=50
data=data.dropna()
#data.drop(columns='Unnamed: 0' ,inplace=True)
value=data.values
#selector = [x for x in range(value.shape[1]) if x != 1]

w_scaler = MinMaxScaler(feature_range=(0, 1))
w_scaler.fit(value[:,:-1])
value[:,:-1] = w_scaler.transform(value[:,:-1])
l_scaler = MinMaxScaler(feature_range=(0, 1))
load_val=value[:,-1].reshape(value.shape[0],1)
l_scaler.fit(load_val)
value[:,-1] = l_scaler.transform(load_val)[:,0]
value=series_to_supervised(value, time_step, n_out)
value=value.values
#f_data=f_data.values
train_X = value[:, :-n_out]
train_y = value[:,-n_out:]
train_X = train_X.reshape((train_X.shape[0],time_step ,n_features ))
last_val=train_X[-1].reshape((1,time_step ,n_features))
prediction=np.array([])
pred_len=40
print('press 0 for training : 1 to load model and predict')
a=int(input())
if not a :
    model = Sequential()
    model.add(LSTM(15, inp1ut_shape=(train_X.shape[1], train_X.shape[2])))
    model.add(Dense(1))
    model.compile(loss='mae', optimizer='adam')
    history = model.fit(train_X, train_y, epochs=10, batch_size=50, verbose=2, shuffle=False)
    save_model('model5_15',model)
else:
    model=load_model('model5_15')
times=np.array([])
for t in range(pred_len):
    pred=model.predict(last_val)[0]
    #print(pred)
    last_time = w_scaler.inverse_transform(last_val[0][-1][:-1].reshape((1,n_features -1)))[0][0]
    #print(last_time)
    fore_index=f_data.index[f_data.iloc[:,0]== round(last_time+5)].tolist()[0]
    next_weather=w_scaler.transform(f_data.ix[fore_index,:].values.reshape((1,n_features -1)))[0]
    #next_step=[next_weather,pred]
    next_step=np.append(next_weather,pred)
    last_val[0] = np.roll(last_val[0], -1, axis=0)
    last_val[0][-1]=next_step
    pred=l_scaler.inverse_transform(pred.reshape((1,n_out)))[0]
    prediction=np.append(prediction,pred)
    times=np.append(times,last_time+5)
#b=np.arange(len(pre),len(prediction)+len(pre))
plt.plot(times,prediction,'.')
a=data.iloc[-2000:,-1]
pre=np.array(a)
l_tim=data.iloc[-2000:,0]
plt.plot(l_tim,pre,'.')
#plt.plot(value[])
plt.show()

