# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

import time
import pandas as pd

import dbConnector as db

chromepath='D:\stuff\chromedriver\chromedriver.exe'

options=webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(chromepath, chrome_options=options)
driver.maximize_window()
mainURL="https://www2.sgx.com/securities/securities-prices"

def retrieveText(lst, attribute="innerText"):
    store=[]
    for i in lst:
        string=i.get_attribute(attribute)
#        if attribute=="href":
#            string=mainURL+string
        store.append(string)
    
    return store

def extractData(df2):
    global lst
    
    names=driver.find_elements_by_class_name('sgx-table-cell-security-name')
    lastPrice=driver.find_elements_by_xpath('//sgx-table-cell-number[@data-column-id="lt"]')
    vol=driver.find_elements_by_xpath("""//sgx-table-cell-number[@data-column-id="vl"]""")
    valTraded=driver.find_elements_by_xpath('//sgx-table-cell-number[@data-column-id="v"]')
    
    lst=vol
    
    df=pd.DataFrame()
    df['names']=retrieveText(names)
    df['last price']=retrieveText(lastPrice)
    df['vol']=retrieveText(vol)
    df['val traded']=retrieveText(valTraded)
    df['address']=retrieveText(names, "href")
    
    df2=df2.append(df)
    df2=df2[df2['names']!='']
    return df2, df

def closeAlerts():
    driver.find_element_by_xpath("//button[text()='OK']").click()
    time.sleep(0.1)
    driver.find_element_by_xpath("//button[text()='Accept Cookies']").click()
    driver.execute_script("window.scrollBy(0,300)")
    
def crawlSummary():
    
    driver.get(mainURL)
    time.sleep(1)
    
    closeAlerts()
    
    time.sleep(0.5)
    
    lst=[]
    df=pd.DataFrame(columns=['names', 'last price', 'vol', 'val traded', 'address'])
    
    df, df2 = extractData(df)
    lst.append(df2)
    
    option=driver.find_element_by_class_name("vertical-scrolling-bar")
    
    for j in range(55):#55
        actionChains = ActionChains(driver)
        actionChains.click_and_hold(option).move_by_offset(0,7.5).release().perform()
        time.sleep(0.2)
        
    #    new_height = driver.execute_script("return arguments[0].scrollHeight", cont)
    #    print(new_height)
        df, df2 = extractData(df)
        lst.append(df2)
        
    df.drop_duplicates(subset ="names", keep = 'first', inplace = True)
    
    df.set_index(pd.Series(list(range(0,len(df)))))
    
    return df, lst

def processData(df):
    vals=pd.DataFrame()
    vals['name']=df['names']
    vals['price']=df['last price']
    
    for i in range(len(vals)):
        try:
            a=float(vals.iloc[i,1])
        except:
            vals.iloc[i,1]=0
    return vals

def processString(info):        
    if info.find('%')==-1 and info!='-':
        symbols=['mm', 'S$', ' ', '(', ')', ',']
        newStr=info
        for i in symbols:
            newStr=newStr.replace(i, '')
            
        try:
            newStr=float(newStr)
        except:
            print('conversion error "%s"'%(info))
            return info
        
        if info.find('mm')>-1:
            newStr=newStr*(10**6)
        
        if info.find('(')>-1:
            newStr=-newStr
    else:
        return info
    
    return newStr

def getCompanyInfo(name, url):
    driver.get(url)

    time.sleep(1)
    #
    try:
        driver.find_element_by_xpath("//button[text()='OK']").click()
        driver.find_element_by_xpath("//button[text()='Accept Cookies']").click()
    except:
        print('click failed')
    #
    time.sleep(1)
    #
    driver.execute_script("window.scrollBy(0,900)")
    #
    driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
    
    overviewDict={
        'openPrice':"""//td[@data-bind="text: companyInfo.openPrice, formatNonZeroValue: 'dollars'"]""",
        'high_low':"""//span[@data-bind="text: companyInfo.lowPrice != null ? companyInfo.lowPrice : '', format: 'dollars'"]""",
        'close':"""//td[@data-bind="text: companyInfo.previousClosePrice, formatNonZeroValue: 'dollars'"]""",
        'prevCloseDate':"""//td[@data-bind="text: companyInfo.previousCloseDate, format: 'date'"]""",
        'marketCap':"""//td[@data-bind="text: companyInfo.marketCap, formatNonZeroValue: 'millions'"]""",
        'mthvwap':"""//span[@data-bind="text: companyInfo.adjustedVolWeightedAvgPrice, formatNonZeroValue: 'number'"]""",
        'sharesOutstanding':"""//td[@data-bind="text: companyInfo.sharesOutstanding, formatNonZeroValue: 'volume'"]""",
        'normalizedEPS':"""//td[@data-bind="text: companyInfo.eps != null ? companyInfo.eps : '-', formatNonZeroValue: 'dollars'"]""",
        'unadjVWAP':"""//td[@data-bind="visible: !companyInfo.hasOwnProperty('volWeightedAvgPrice') || companyInfo.volWeightedAvgPrice == null"]""",
        'adjVWAP':"""//td[@data-bind="visible: !companyInfo.hasOwnProperty('adjustedVolWeightedAvgPrice') || companyInfo.adjustedVolWeightedAvgPrice == null"]"""
        }
    
    valuationDict={
        'peratio':"""//td[@data-bind="text: companyInfo.peRatio != null ? companyInfo.peRatio : '-', formatNonZeroValue: 'number'"]""",
        'evebita':"""//td[@data-bind="text: companyInfo.evEbitData != null ? companyInfo.evEbitData : '-', formatNonZeroValue: 'number'"]""",
        'pricebookvalue':"""//td[@data-bind="text: companyInfo.priceToBookRatio != null ? companyInfo.priceToBookRatio : '-', formatNonZeroValue: 'number'"]""",
        'dividend':"""//td[@data-bind="text: companyInfo.dividendYield != null ? companyInfo.dividendYield : '-', formatNonZeroValue: 'percent'"]"""
        }
    
    financialsDict={
        'debtebita':"""//td[@data-bind="text: companyInfo.totalDebtEbitda != null ? companyInfo.totalDebtEbitda : '-', formatNonZeroValue: 'number'"]""",
        'debt':"""//td[@data-bind="text: companyInfo.totalDebt != null ? companyInfo.totalDebt : '-', formatNonZeroValue: 'millions'"]""",
        'enterpriseValue':"""//td[@data-bind="text: companyInfo.enterpriseValue != null ? companyInfo.enterpriseValue : '-', formatNonZeroValue: 'millions'"]""",
        'assets':"""//td[@data-bind="text: companyInfo.totalAssets != null ? companyInfo.totalAssets : '-', formatNonZeroValue: 'millions'"]""",
        'cash':"""//td[@data-bind="text: companyInfo.cashInvestments != null ? companyInfo.cashInvestments : '-', formatNonZeroValue: 'millions'"]""",
        'capEx':"""//td[@data-bind="text: companyInfo.capitalExpenditures != null ? companyInfo.capitalExpenditures : '-', formatNonZeroValue: 'millions'"]""",
        'EBIT':"""//td[@data-bind="text: companyInfo.ebit != null ? companyInfo.ebit : '-', formatNonZeroValue: 'millions'"]""",
        'revenue':"""//td[@data-bind="text: companyInfo.totalRevenue != null ? companyInfo.totalRevenue : '-', formatNonZeroValue: 'millions'"]""",
        'netincome':"""//td[@data-bind="text: companyInfo.netIncome != null ? companyInfo.netIncome : '-', formatNonZeroValue: 'millions'"]""",
        'ebita':"""//td[@data-bind="text:  companyInfo.ebitda != null ? companyInfo.ebitda : '-', formatNonZeroValue: 'millions'"]"""
        }
    
    allDict={
        'overview':overviewDict,
        'valuation':valuationDict,
        'financials':financialsDict
        }
    
    dividendsDict={
        'date':"""//td[@data-bind="text: dividendExDate, format: 'date'"]""",
        'dividend':"""//td[@data-bind="text: dividendPrice, formatNonZeroValue: 'cents'"]"""
            }
    
    store={}
    processedStore={}
    storeDF=pd.DataFrame()
    storeDF['name']=[name]
    
    for j in allDict:
        oneDict=allDict[j]
        tem={}
        tem2={}
        for i in oneDict:
            try:
                info=driver.find_element_by_xpath(oneDict[i]).get_attribute('innerText')
            except:
                info='-'
            tem[i]=info
            tem2[i]=processString(info)
            storeDF[i]=[tem2[i]]
        store[j]=tem
        processedStore[j]=tem2
    
    dates=driver.find_elements_by_xpath(dividendsDict['date'])
    dividends=driver.find_elements_by_xpath(dividendsDict['dividend'])
    
    dividendList=pd.DataFrame(columns=['date', 'dividend'])
    for i in range(len(dates)):
        date=dates[i].get_attribute('innerText')
        dividend=dividends[i].get_attribute('innerText')
        dividendList.loc[i]=[date, dividend]
        if i == 0:
            storeDF['dividend']=dividend
        
    return storeDF, store, processedStore, dividendList

def getTime(prev):
    cur=time.time()
    return cur, str((time.time()-prev)/60)

def collateCompanyInfo(comList, fname='companyInfo.csv'):
    cur, elapsedTime=getTime(start)
    
    print('got list of companies in %s mins'%(elapsedTime))
    
    store=''
    
    for i in range(len(comList)):
        name=comList.iloc[i,0]
        url=comList.iloc[i,4]
        cur, elapsedTime=getTime(cur)
        print('processing %s: %s in %s mins'%(str(i), name, elapsedTime))
        cur=time.time()
        companyinfo=getCompanyInfo(name, url)
        if i ==0:
            store=companyinfo[0]
        else:
            store.loc[i]=companyinfo[0].loc[0]
            print(store.loc[i])
    
    cur, elapsedTime=getTime(start)        
    print('total time: %s mins'%(elapsedTime))
    
    store.to_csv(fname, index=False)
    
    return store

start=time.time()
df, df2=crawlSummary()
#
#vals=processData(df)
#db.updateDB(vals)

companyFullInfo=collateCompanyInfo(df)
    