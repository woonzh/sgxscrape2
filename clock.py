# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 18:28:55 2017

@author: ASUS
"""

from apscheduler.schedulers.blocking import BlockingScheduler
import master

sched = BlockingScheduler()

#@sched.scheduled_job('interval', days=7)
#def timed_job():
#    print('This job is run every week.')

#@sched.scheduled_job('cron', day_of_week='mon-fri', hour=12)
#def scheduled_job():
#    msg=master.updateSGXPrice()
#    
#    print('success')
    
@sched.scheduled_job('interval', minute=15)
def scheduled_job():
    msg=master.updateSGXPrice()
    
    print('success')

sched.start()