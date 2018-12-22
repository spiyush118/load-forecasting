from math import sqrt
from numpy import concatenate
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
from func import *
import os
import glob
n_features=5
#data=pd.read_csv('final_data.csv')
#data=final_data()
data=pd.read_csv(r'C:\Users\piyush suman\Desktop\explo\final_data.csv')
n_train_time=20001
time_step=20
n_out=10
batch_size=50
data=data.dropna()
value=data.values
scaler = MinMaxScaler(feature_range=(0, 1))
value = scaler.fit_transform(value)
value=series_to_supervised(value, time_step, n_out)
value=value.values
train = value[1:n_train_time, :]
test = value[n_train_time:30001, :]

# split into input and outputs
train_X, train_y = train[:, :-n_out], train[:, -n_out]
test_X, test_y = test[:, :-n_out], test[:, -n_out]

# reshape input to be 3D [samples, timesteps, feaatures]
train_X = train_X.reshape((train_X.shape[0],time_step ,n_features ))
test_X = test_X.reshape((test_X.shape[0],time_step, n_features))
model = Sequential()
model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
model.add(Dense(1))
model.compile(loss='mae', optimizer='adam')
history = model.fit(train_X, train_y, epochs=25, batch_size=50, validation_data=(test_X, test_y), verbose=2, shuffle=False)

# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()

# make a prediction
yhat = model.predict(test_X)
test_X = test_X.reshape((test_X.shape[0], n_features*time_step))
t1=test_X[:,:n_features]
yhat=yhat.reshape(yhat.shape[0])
t1[:,1]=yhat

inv_yhat = scaler.inverse_transform(t1)
inv_yhat = inv_yhat[:,1]

t2=test_X[:,:n_features]
test_y=test_y.reshape(test_y.shape[0])
t2[:,1]=test_y
inv_y = scaler.inverse_transform(t2)
inv_y = inv_y[:,1]
# calculate RMSE

##plt.plot(range(len(inv_y)),inv_y)
##plt.plot(range(len(inv_yhat)),inv_yhat)
##plt.show()
rmse = np.sqrt(mean_squared_error(inv_y, inv_yhat))
print('Test RMSE: %.3f' % rmse)
