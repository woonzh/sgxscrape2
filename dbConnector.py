# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 23:11:08 2018

@author: ASUS
"""

import os
from urllib import parse
import psycopg2 as ps

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

def runquery(query):
    cur, conn=connectToDatabase()
    result=None
    try:
        cur.execute(query)
        result=list(cur)
    except:
        result=['error']
        
    cur.close()
    conn.commit()
    return result

#lst=['test','def']
#lst.sort()
#
#query="SELECT name from PRICE"
#names = [i[0] for i in runquery(query)]
#names.sort()
#
#addList=[]
#
#for i in lst:
#    try:
#        names.remove(i)
#    except:
#        addList.append(i)
        
query="SELECT column_name FROM information_schema.columns WHERE table_name = 'price'"
colNames=str([i[0] for i in runquery(query)])[1:-1]

#query="INSERT INTO price(%s) VALUES %s" % (colNames)
    