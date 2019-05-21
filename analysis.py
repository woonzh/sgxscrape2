# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 21:54:43 2019

@author: ASUS
"""

import os
import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.neighbors import LocalOutlierFactor
import matplotlib.pyplot as plt

file='data/companyInfo(updated).csv'
newFile='data/companyInfo(cleaned).csv'
summaryFName='data/summary.csv'
filedir='logs'
metadata = 'D:\stuff\scrapy\sgx\logs\metadata.txt'
pca = PCA(n_components=3,#len(list(dfProcess)),
         random_state = 123,
         svd_solver = 'auto'
         )
clf = LocalOutlierFactor(contamination=0.3)

def replace(string, old, new):
    string.replace(old, new)

def dfCleaner(df, cleanCol='prevCloseDate', exceptions=[]):
    dfNew=df[df[cleanCol]!='-']
    dfDel=df[df[cleanCol]=='-']
    print('%s with empty values deleted.'%(len(dfDel)))
    
    df=dfNew.copy(deep=True)
    
    summary=pd.DataFrame(columns=['name','count', 'percen'])
    
    for header in list(df):
        if header not in exceptions:
#            print(header)
            lst=list(df[header])
            newLst=[]
            for i in lst: 
                i=str(i)                   
                if 'M' in i or 'B' in i:
                    newVal=i.replace(',', '')
                    if 'M' in newVal:
                        newVal=newVal.replace('M', '')
                        try:
                            newVal=float(newVal)*1000000
                        except:
                            newVal=0
                    else:
                        newVal=newVal.replace('B', '')
                        try:
                            newVal=float(newVal)*1000000000
                        except:
                            newVal=0
                        
                else:
                    newVal=i.replace('USD', '')
                    newVal=i.replace('SGD', '')
                    try:
                        newVal=float(newVal)
                    except:
                        newVal=0
                
                newLst.append(newVal)
            df[header]=newLst
            errorCount=sum(df[header]==0)
            summary.loc[len(summary)]=[header, errorCount,round(errorCount/len(df),1)]
    return df, dfDel, dfNew, summary

def featuresEngineering(df, details):
    eps=df['normalizedEPS']
    price=df['openPrice']
    income=df['netincome']
    cash=df['cash']
    assets=df['assets']
    debt=df['debt']
    enterpriseVal=df['enterpriseValue']
    sharesOutstanding=df['sharesOutstanding']
    
    #new PEratio
    df['new PE ratio']=[x/(y/z) if (x!=0 and y!=0 and z!=0) else 0 for x, y,z in zip(price,income, sharesOutstanding)]
    
#    #pricebook value
#    df['pbvratio']=[c/((x+y+z-a)/b) if (x!=0 and y!=0 and z!=0 and a!=0 and b!=0 and c!=0) else 0 \
#      for x, y, z, a, b, c in zip(cash, assets, enterpriseVal, debt, outstandingshares, closePrice)]
#    
#    #enterprice value over ebita
#    newebita=[x if x!=0 else y for x, y in zip(ebita, income)]
#    df['newevebita']=[x/y if (x!=0 and y!=0) else 0 for x, y in zip(enterpriseVal, newebita)]
#    
#    #ROE
    df['new roe']=[x/(y+z-a) if (x!=0 and y!=0 and z!=0 and a!=0) else 0 \
      for x, y, z, a in zip(income, cash, assets, debt)]

#    #ROA
    df['new roa']=[x/y if (x!=0 and y!=0) else 0 \
      for x, y in zip(income, assets)]
#    #aquirer multiple
    df['aquirer multiple']=[x/y if (x!=0 and y!=0) else 0 for x, y in zip(income, enterpriseVal) ]
    
#    #aquirer multiple against price
    df['normalized aquirer multiple']=[y/x if (x!=0 and y!=0) else 0 for x,y in zip(df['aquirer multiple'], price)]
    
    df=pd.merge(df, details[['names','address']], how='left',left_on='name',right_on='names')
    
    df=df.drop(['names'], axis=1)
    return df

def removeNull(df, inclusions=[]):
    newDf=pd.DataFrame(columns=list(df))
    if inclusions==[]:
        inclusions=list(range(len(list(df))))
    
    for i in list(df.index):
        val=list(df.loc[i][inclusions])
        if 0 not in val:
            newDf.loc[i]=df.loc[i]
            
    newDf=newDf.reset_index(drop=True)
    return newDf

def pcaFiles(df):
    df_pca_main = pd.DataFrame(pca.fit_transform(df))
    df_pca = df_pca_main.values
    return df_pca

def removeOutlier(df, orgDf):
    clf = LocalOutlierFactor(contamination=0.3)
    y_pred = clf.fit_predict(df)
    
    newdf2=pd.DataFrame(columns=list(orgDf))
    for count, val in enumerate(list(y_pred)):
        if val==1:
            newdf2.loc[count]=list(orgDf.loc[count])
    
    return newdf2

def plotKMeans(df, clusters=1):
    kmeans = KMeans(n_clusters=clusters)
    kmeans.fit(df)
    
    # appropriate cluster labels of points in ds
    data_labels = kmeans.labels_
    # coordinates of cluster centers
    cluster_centers = kmeans.cluster_centers_
    
    colors = ['b', 'g']
    plt.scatter(df[:, 0], df[:, 1],
                            c=[colors[i] for i in data_labels], s=1)
    plt.scatter(cluster_centers[:, 0], cluster_centers[:, 1], color = "k")
    plt.show()
    
def cleanAndProcess(sumName=summaryFName, infoName=file, newFileName=newFile):
    details=pd.read_csv(sumName)
    df=pd.read_csv(infoName)
    
    dfMain, dfDel, dfCheck, summary=dfCleaner(df, exceptions=['name', 'prevCloseDate', 'float'])
    dfNew=featuresEngineering(dfMain, details)
    
    dfNew.to_csv(newFileName, index=False)
    dfNew=dfNew.set_index(dfNew['name'], drop=True)
    
    dfCompare=dfNew[['name', 'address','openPrice', 'normalizedEPS', 'peratio', 'new PE ratio', 'netincome', 'operating_margin', 'net_profit_margin','aquirer multiple','normalized aquirer multiple', 'cash', 'assets', 'roe', 'new roe', 'roa', 'new roa', 'price/Sales', 'price/CF','long term debt/equity', 'revenue_per_share_5_yr_growth', 'eps_per_share_5_yr_growth']]
    a=dfCompare[(dfCompare['peratio']>0)&(dfCompare['openPrice']>0.2)]
    
    return dfMain, dfDel, dfCheck, summary, dfNew, dfCompare, a

if __name__ == "__main__":
    dfMain, dfDel, dfCheck, summary, dfNew, dfCompare, a=cleanAndProcess(summaryFName, file, newFile)
#

#df=dfNew[['name', 'openPrice', 'close', 'dividend', 'pricebookvalue','new PE ratio', 'margin', 'newevebita', 'roe']]
#df2=removeNull(df, [4,5,6,7])
#dfProcess=df2[['dividend', 'pricebookvalue','new PE ratio', 'margin', 'newevebita', 'roe']]
#
#df_pca = pcaFiles(dfProcess)
#
#newdf2=removeOutlier(df_pca, df2)
#newdfProcess=newdf2[['dividend', 'pricebookvalue','new PE ratio', 'margin', 'newevebita', 'roe']]
#newdf2.to_csv()
#
#df_pca = pcaFiles(newdfProcess)
#
#plotKMeans(df_pca)
#
#compare=dfNew[['name','peratio', 'new PE ratio', 'enterpriseValue', 'EBIT','aquirer multiple', 'ebita', 'netincome', 'roe']]
#compare=compare[(compare['aquirer multiple']!=0) & (compare['EBIT']>0)]

#tf_data = tf.Variable(df_pca)
#
#with tf.Session() as sess:
#    saver = tf.train.Saver([tf_data])
#    sess.run(tf_data.initializer)
#    saver.save(sess, filedir+'/tf_data.ckpt')
#    config = projector.ProjectorConfig()
#    embedding = config.embeddings.add()
#    embedding.tensor_name = tf_data.name
#    embedding.metadata_path = metadata
#    projector.visualize_embeddings(tf.summary.FileWriter(filedir), config)