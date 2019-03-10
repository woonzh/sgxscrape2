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

def replace(string, old, new):
    string.replace(old, new)

def dfCleaner(df, exceptions=[]):
    for header in list(df):
        if header not in exceptions:
#            print(header)
            lst=list(df[header])
            newLst=[]
            for i in lst:
                newVal=i.replace('S$', '')
                try:
                    newVal=float(newVal)
                except:
                    newVal=0
                
                newLst.append(newVal)
            df[header]=newLst
    return df

def featuresEngineering(df):
    rev=df['revenue']
    outstandingshares=df['sharesOutstanding']
    income=df['netincome']
    closePrice=df['close']
    cash=df['cash']
    assets=df['assets']
    enterpriseVal=df['enterpriseValue']
    debt=df['debt']
    ebita=df['ebita']
    
    
    #margin
    df['margin']=[x/y if (x!=0 and y!=0) else 0 for x, y in zip(income, rev)]
    
    #new PEratio
    df['new PE ratio']=[z/(x/y) if (x!=0 and y!=0 and z!=0) else 0 for x, y, z in zip(income, outstandingshares, closePrice)]
    
    #pricebook value
    df['pbvratio']=[c/((x+y+z-a)/b) if (x!=0 and y!=0 and z!=0 and a!=0 and b!=0 and c!=0) else 0 \
      for x, y, z, a, b, c in zip(cash, assets, enterpriseVal, debt, outstandingshares, closePrice)]
    
    #enterprice value over ebita
    newebita=[x if x!=0 else y for x, y in zip(ebita, income)]
    df['newevebita']=[x/y if (x!=0 and y!=0) else 0 for x, y in zip(enterpriseVal, newebita)]
    
    #ROE
    df['roe']=[x/(y+z-a) if (x!=0 and y!=0 and z!=0 and a!=0) else 0 \
      for x, y, z, a in zip(income, cash, assets, debt)]
    
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
    
def runNeural(df):
    graph=tf.graph()
    with graph.as_default():
        

file='companyInfo.csv'
filedir='logs'
metadata = 'D:\stuff\scrapy\sgx\logs\metadata.txt'
pca = PCA(n_components=3,#len(list(dfProcess)),
         random_state = 123,
         svd_solver = 'auto'
         )
clf = LocalOutlierFactor(contamination=0.3)

dfMain=dfCleaner(pd.read_csv(file), ['name', 'prevCloseDate'])
dfNew=featuresEngineering(dfMain)
df=dfNew[['name', 'openPrice', 'close', 'dividend', 'pricebookvalue','new PE ratio', 'margin', 'newevebita', 'roe']]
df2=removeNull(df, [4,5,6,7])
dfProcess=df2[['dividend', 'pricebookvalue','new PE ratio', 'margin', 'newevebita', 'roe']]

df_pca = pcaFiles(dfProcess)

newdf2=removeOutlier(df_pca, df2)
newdfProcess=newdf2[['dividend', 'pricebookvalue','new PE ratio', 'margin', 'newevebita', 'roe']]
newdf2.to_csv(metadata, sep='\t')

df_pca = pcaFiles(newdfProcess)

plotKMeans(df_pca)

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