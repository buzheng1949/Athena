# coding=utf-8
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import time
import datetime
from docopt import docopt
import sys


'''获取指定时间 方式 的数据'''
def hub_message(start,end,get_type):
    article_messages = ''
    url = 'https://api.readhub.me/wechat/topics?'
    start = start +'000'
    end = end + '999' #没办法 接口如此
    ret = requests.get(url,params={'start':start,'end':end,'type':get_type})
    if ret.status_code == 200:
        article_messages = ret.json()
    return article_messages

"""解析文章"""
def parse_article(messages):
    messages_list = {}
    total_message = ''
    for article in messages['data']:
        title = '<font color=red><b>'+'★  '+article['title']+'</b></font>' 
        detail = '<br>'+article['summary']+'</br>'
        total_message += title
        total_message += detail
    return total_message

"""发送邮件"""
def mail(sender,receiver,password,news):
    ret = True
    try:
        message = MIMEText(news,_subtype='html',_charset='utf-8') # 发送的内容
        message['Subject'] = '邮件主题'
        message['From'] = formataddr(['昵称昵称',sender])
        message['To'] = formataddr(['昵称昵称',receiver])
        server = smtplib.SMTP_SSL('smtp.qq.com',465)
        server.login(sender,password)
        server.sendmail(sender,[receiver,],message.as_string())
        server.quit()
    except :
        ret =False
    return ret
    

'''执行定时任务'''
def job(job_hour,job_minute):
    while True:
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        if job_hour == hour and job_minute == minute:
            cur_time = int(time.time())
            lingcheng = str(cur_time - cur_time%(24*60*60)-(24*60*60))
            tomorrow = str(cur_time - cur_time%(24*60*60) + (24*60*60))
            articles = hub_message(lingcheng,tomorrow,'day')
            news = parse_article(articles)
            sender = 'the sender \'s email'
            receiver = 'the receiver \'s email'
            password = 'your password' # 你的密码
            if mail(sender,receiver,password,news):
                print ('send the news success')
            else:
                print ('send the news fail')
        else:
            print ('time is evil,hour = %s,minute =%s '%(hour,minute))
        time.sleep(60) # 60s查询一次

"""结合crontab 定时任务使用这个方法"""
def send_with_crontab():
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    cur_time = int(time.time())
    lingcheng = str(cur_time - cur_time%(24*60*60)-(24*60*60))
    tomorrow = str(cur_time - cur_time%(24*60*60) + (24*60*60))
    articles = hub_message(lingcheng,tomorrow,'day')
    news = parse_article(articles)
    sender = 'the sender \'s email'
    receiver = 'the receiver \'s email'
    password = 'your password' # 你的密码
    if mail(sender,receiver,password,news):
        print ('send the news success')
    else:
        print ('send the news fail')

"""函数入口"""
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    # job(0,0) #定时凌晨一分钟查询
    send_with_crontab()
  