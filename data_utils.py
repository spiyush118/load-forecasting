import numpy as np
from matplotlib import pyplot
from pandas import read_csv
from pandas import DataFrame
from pandas import concat,merge
import pandas as pd 
import os
import glob
import collections
import pickle
def test_apply(x):
    try:
        return float(x)
    except ValueError:
        return np.nan
def temp_edit(x):
    st=x[:-2]
    p=int(st)
    i=(p-32)*5.0/9.0
    return i
def cond_edit(data):
    labels=list(data.Conditions.unique())
    map = dict(zip(labels, range(len(labels))))
    data['Conditions']=data['Conditions'].apply(lambda s: map.get(s) if s in map else s)
    return data
def time_edit(st):
    a=int(st[0:-6])
    b=int(st[-5:-3])
    if (st[-2:]=='AM' or st[-2:]=='am') and st[0:-6]=='12':
        a=0
    if (st[-2:]=='PM' or st[-2:]=='pm')and st[0:-6]!='12':   
        a+=12
    return 60*a+b
def humid_edit(x):
    try:
       return int(x.strip('%').strip(' '))
    except ValueError :
        return np.nan
def get_weather(path):
    data=read_csv(path,usecols=['Time (IST)','Temp.','Humidity','Conditions'])
    #data1=read_csv(r"C:\Users\piyush suman\Desktop\explo\Whether_Data\2017\10\03-10-2017.csv",usecols=['Temp.',','Humidity','Conditions'])
    
    data['Time (IST)']=data['Time (IST)'].apply(time_edit)
    data['Humidity']=data['Humidity'].apply(humid_edit)
    
    data['Temp.']=data['Temp.'].apply(test_apply)
    return data
def repeat(data):
    newdataset=data.ix[0]
    for j in range(5,int(data.ix[1]['Time (IST)'])-int(data.ix[0]['Time (IST)']),5):
            dataset=data.ix[0].copy()
            dataset['Time (IST)']+=j
            newdataset=concat([newdataset,dataset],axis=1)
    
    for i in range(1,data.shape[0]-1):
        dataset=data.ix[i].copy()
        newdataset=concat([newdataset,dataset],axis=1)
        for j in range(5,int(data.ix[i+1]['Time (IST)'])-int(data.ix[i]['Time (IST)'])-1,5):
            dataset=data.ix[i].copy()
            dataset['Time (IST)']+=j
            newdataset=concat([newdataset,dataset],axis=1)

##    for j in range(5,int(data.ix[-1]['Time (IST)'])-int(data.ix[-2]['Time (IST)']),5):
##            dataset=data.ix[data.shape[0]-1].copy()
##            dataset['Time (IST)']-=j
##            newdataset=concat([newdataset,dataset],axis=1)
    dataset=data.ix[data.shape[0]-1].copy()
    newdataset=concat([newdataset,dataset],axis=1)
    newdataset=newdataset.T
    newdataset= newdataset.rename(columns={'Time (IST)':'time'})
    return newdataset
    
   
def series_to_supervised(data, n_in=1, n_out=1,dropnan=True):
	n_vars = 1 if type(data) is list else data.shape[1]
	dff = pd.DataFrame(data)
	cols, names = list(), list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(dff.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	##forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(dff.iloc[:,-1].shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_out)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_out)]
	# put it all together
	agg = pd.concat(cols, axis=1)
	agg.columns = names
	#drop rows with NaN values
	if dropnan:
		agg.dropna(inplace=True)
	return agg
def get_load(path):
    data=read_csv(path)
    
    data.time=data.time.apply(lambda x:int(x[0:2])*60+int(x[3:]))
    data.astype('float32')

    return data
def get_fore_weather(path):
    data=read_csv(path , usecols=["0","1","2","8"])
    data.dropna(inplace=True)
    data['0']=data['0'].apply(time_edit)
    data['8']=data['8'].apply(humid_edit)
    data['2']=data['2'].apply(temp_edit)
    data.columns=['Time (IST)','Conditions','Temp.','Humidity']
    df=data.loc[:,[ 'Time (IST)', 'Temp.', 'Humidity', 'Conditions']]
    #df=df.rename(columns={'Time (IST)':'time'})
    df.index=range(data.shape[0])
    return df
def file_list():
    my_path = os.path.dirname(__file__)
    load_path=os.path.join(my_path, "SLDC_Data")
    weather_path=os.path.join(my_path, "Whether_Data")
    os.chdir(load_path)
    load=glob.glob('*/*/*.csv')
    os.chdir(weather_path)
    weather=glob.glob('*/*/*.csv')
    os.chdir(my_path)
    a = collections.OrderedDict.fromkeys(load)
    b = collections.OrderedDict.fromkeys(weather)
    return a,b

def final_data(Data,s_load,s_weather):
    my_path = os.path.dirname(__file__)
    fore_path=os.path.join(my_path, "forecasted_weather.csv")
    load_path=os.path.join(my_path, "SLDC_Data")
    weather_path=os.path.join(my_path, "Whether_Data")
    #p_list=load_list()
    p_list=[]
    load,weather=file_list()
    a=list(s_load.items())
    b=list(s_weather.items())
    l=0
    l_index=0
    m_index=0
    if not len(a)==0 :
        last_load=a[-1][0]
        last_weather=b[-1][0]
        l_index=list(load.keys()).index(last_load)
        m_index=list(weather.keys()).index(last_weather)
    else:
        l_index=0
        m_index=0
    w_Data=Data.copy()
    load=list(load.keys())[l_index:]
    weather=list(weather.keys())[m_index:]
    #dates=list(set(load).intersection(weather))-
    #Data=DataFrame()
    w_set = frozenset(weather)
    dates = [x for x in load if x in w_set]
    print(load==weather)
    #dates=weather
    print(len(dates))
    f_data=get_fore_weather(fore_path)
    
    for index,date in enumerate(dates):
        print(index)
        print(date)
        data=get_weather(os.path.join(weather_path,date))
        data1=get_load(os.path.join(load_path,date))
        if index==len(dates)-1 :
            t_last=data1['time'].iloc[-1]
            dat=concat([data,f_data],axis=0)
            dat.index=range(dat.shape[0])
            #d=dat.copy()
            data=repeat(dat)
            data.index=range(data.shape[0])
            print("______")
            fore_index=data.index[data['time']== t_last].tolist()[0]
            f_data=data.ix[fore_index:].copy()
        else:
            data=repeat(data)
            print("______")
        
        data3=merge(data,data1,on='time',how='inner')
        print(data3.columns)
        data3=DataFrame.drop_duplicates(data3,subset='time',keep='first')
        Data=concat([Data,data3],axis=0)
        if index==len(dates)-2 :
            w_Data=Data.copy()
            print("df")
    Data.index=range(Data.shape[0])
    #Data,map=cond_edit(Data)

    Map,n_list=final_map(p_list,Data,f_data)
    saving_list(n_list)
    f_data['Conditions']=f_data['Conditions'].apply(lambda s: Map.get(s) if s in Map else s)
    Data['Conditions']=Data['Conditions'].apply(lambda s: Map.get(s) if s in Map else s)
    w_Data['Conditions']=w_Data['Conditions'].apply(lambda s: Map.get(s) if s in Map else s)
    Data.applymap(test_apply).dropna(inplace=True)
    f_data.applymap(test_apply).dropna(inplace=True)
    #f_data=repeat(f_data)
    Data.astype('float32')
##    w_Data=Data.copy().ix[:l+len(set(s_load).intersection(s_weather))]
    w_Data.to_csv('final_data1.csv',index=False)
    f_data.astype('float32')
    return Data,f_data
def final_map(p_list,data1,data2):
    labels=[]
    label1=list(data1.Conditions.unique())
    label2=list(data2.Conditions.unique())
    labels.extend(label1)
    labels.extend(label2)
    labels.extend(p_list)
    labels=list(set(labels))
    Map = dict(zip(labels, range(len(labels))))
    return Map,labels

def saving_list(list_cond):
    with open('parrot.pkl', 'wb') as f:
        pickle.dump(list_cond,f)    
    
def load_list():
    with open('parrot.pkl', 'rb') as f:
        mynewlist = pickle.load(f)
        return mynewlist



