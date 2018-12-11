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

df, df2=crawlSummary()
#
vals=processData(df)
db.updateDB(vals)

#url='https://www2.sgx.com/securities/stock-screener?page=1&code=500'
#url='https://sgx-premium.wealthmsi.com/company-tearsheet.html?page=1&code=500#https%3A%2F%2Fwww2.sgx.com%2Fsecurities%2Fstock-screener%3Fpage%3D1%26code%3D500'

#driver.get(url)
#
#time.sleep(1)
#
#driver.find_element_by_xpath("//button[text()='OK']").click()
#driver.find_element_by_xpath("//button[text()='Accept Cookies']").click()
#
#time.sleep(1)
#
#driver.execute_script("window.scrollBy(0,900)")
#
#time.sleep(1)
#
#driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
#
#marketCap=driver.find_element_by_xpath("""//span[@data-bind="text: companyInfo.volWeightedAvgPrice, formatNonZeroValue: 'number'"]""").get_attribute("innerText")
#mthvwap=driver.find_element_by_xpath("""//span[@data-bind="text: companyInfo.adjustedVolWeightedAvgPrice, formatNonZeroValue: 'number'"]""").get_attribute("innerText")
#sharesOutstanding=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.sharesOutstanding, formatNonZeroValue: 'volume'"]""").get_attribute("innerText")
#eps=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.eps != null ? companyInfo.eps : '-', formatNonZeroValue: 'dollars'"]""").get_attribute("innerText")
#
#peratio=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.peRatio != null ? companyInfo.peRatio : '-', formatNonZeroValue: 'number'"]""").get_attribute("innerText")
#evebita=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.evEbitData != null ? companyInfo.evEbitData : '-', formatNonZeroValue: 'number'"]""").get_attribute("innerText")
#pricebookvalue=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.priceToBookRatio != null ? companyInfo.priceToBookRatio : '-', formatNonZeroValue: 'number'"]""").get_attribute("innerText")
#dividend=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.dividendYield != null ? companyInfo.dividendYield : '-', formatNonZeroValue: 'percent'"]""").get_attribute("innerText")
#evebit=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.evEbitData != null ? companyInfo.evEbitData : '-', formatNonZeroValue: 'number'"]""").get_attribute("innerText")
#
#debtebita=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.totalDebtEbitda != null ? companyInfo.totalDebtEbitda : '-', formatNonZeroValue: 'number'"]""").get_attribute("innerText")
#assets=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.totalAssets != null ? companyInfo.totalAssets : '-', formatNonZeroValue: 'millions'"]""").get_attribute("innerText")
#cash=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.cashInvestments != null ? companyInfo.cashInvestments : '-', formatNonZeroValue: 'millions'"]""").get_attribute("innerText")
#revenue=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.totalRevenue != null ? companyInfo.totalRevenue : '-', formatNonZeroValue: 'millions'"]""").get_attribute("innerText")
#netincome=driver.find_element_by_xpath("""//td[@data-bind="text: companyInfo.netIncome != null ? companyInfo.netIncome : '-', formatNonZeroValue: 'millions'"]""").get_attribute("innerText")
#ebita=driver.find_element_by_xpath("""//td[@data-bind="text:  companyInfo.ebitda != null ? companyInfo.ebitda : '-', formatNonZeroValue: 'millions'"]""").get_attribute("innerText")
#
#valuation=driver.find_element_by_xpath('//td[@data-id="valuation"]').get_attribute("class")
