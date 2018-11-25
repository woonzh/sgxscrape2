# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 23:11:08 2018

@author: ASUS
"""

import os
from urllib import parse
import psycopg2 as ps
from datetime import datetime
import pandas as pd

def connectToDatabase():
    url='postgres://bmmoobheozofxs:ac8ba0f76a53e13844126695d8bad3d6826d1e087773b87bef85cebc43664f30@ec2-54-225-196-122.compute-1.amazonaws.com:5432/d20apms1nhd8do'

    os.environ['DATABASE_URL'] = url
               
    parse.uses_netloc.append('postgres')
    url=parse.urlparse(os.environ['DATABASE_URL'])
    
    conn=ps.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
            )
    
    cur=conn.cursor()
    
    return cur, conn

def runquery(query, lst=True, connected=False, connList={}):
    if connected:
        cur=connList['cur']
        conn=connList['conn']
    else:
        cur, conn=connectToDatabase()
        
    result=None
    try:
        cur.execute(query)
        if lst:
            result=list(cur)
        else:
            result=['success']
    except:
        result=['error']
    
    print(result)
    
    if connected==False:
        cur.close()
        conn.commit()
    return result

def updateCompanyRows(lst, connList):    
    lst.sort()
    
    #get current company names and new names to add
    query="SELECT name from PRICE"
    names = [i[0] for i in runquery(query, connected=True, connList=connList)]
    names.sort()
    
    addList=[]
    
    for i in lst:
        try:
            names.remove(i)
        except:
            addList.append(i)
    
    #get all column names
    query="SELECT column_name FROM information_schema.columns WHERE table_name = 'price'"
    colNames=[i[0] for i in runquery(query, connected=True, connList=connList)]
    
    #create new row
    if len(addList)>0:
        query="INSERT INTO price(%s) VALUES (%s)" % (str(colNames)[1:-1].replace("'",""), str(addList+[0]*(len(colNames)-1))[1:-1])
        result=runquery(query,lst=False, connected=True, connList=connList)
    else:
        result=["table already up to date."]
    
    return result

def createNewRow(connList):
    curDate=datetime.now()
    colName="date%s%s%s"%(curDate.day, curDate.month, curDate.year)
    query="ALTER TABLE price ADD %s float"%(colName)
    
    print(query)
    
    result=runquery(query, lst=False, connected=True, connList=connList)
    return result, colName

def updatePrice(df, connList, colName):
    t=1
    query="CREATE TEMPORARY TABLE tem(name VARCHAR(255), price FLOAT)"
    print(query)
    result=runquery(query, lst=False, connected=True, connList=connList)
    df.to_sql("tem", connList['conn'])
    print("copied df to temp")
    query="UPDATE price JOIN tem ON tem.name = price.name SET price.%s = tem.price"%(colName)
    print(query)
    result=runquery(query, lst=False, connected=True, connList=connList)
    
    return result

def updateDB(df):
    cur, conn=connectToDatabase()
    connList={
        'cur': cur,
        'conn': conn
        }
    try:
        comNames=list(df['name'])
        if updateCompanyRows(comNames, connList)[0] =='error':
            return False, 'error updating / checking companies in DB'
        else:
            result, colName=createNewRow(connList)
            result2=updatePrice(df)
    except:
        cur.close()
        conn.commit()  
    
    cur.close()
    conn.commit()
    

#result=updateCompanyRows(['def7', 'test'])

df=pd.DataFrame(columns=['name', 'price'])
df.loc[0]=['def', '110.0']
df.loc[1]=['test', '112.0']
#updateDB(df)

cur, conn=connectToDatabase()
connList={
    'cur': cur,
    'conn': conn
    }
try:
    comNames=list(df['name'])
    result=updateCompanyRows(comNames, connList)
    if result[0] =='error':
        t=1
#        return False, 'error updating / checking companies in DB'
    else:
        result, colName=createNewRow(connList)
        print('test')
        result2=updatePrice(df, connList, colName)
except:
    cur.close()
    conn.commit()  

cur.close()
conn.commit()