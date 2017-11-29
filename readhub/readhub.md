#### 如何实现一个自动抓取readhub的脚本
**项目地址:[自动抓取readhub源代码](https://github.com/buzheng1949/Athena/tree/master/readhub)**
##### 一、需求分析
 - 抓取新闻来源 
 - 定时抓取数据
 - 发送数据到邮箱
 
##### 二、步骤拆解
 - 如何获取数据
 
  - 在获取数据方面，我们采用Charles抓包的方式，首先微信搜索readhub小程序，然后点击的时候，我们可以发现readhub的API接口为**https://api.readhub.me/wechat/topics?start=1511481600000&end=1511568000999**
  - 获取数据之后，需要对数据进行解析，访问该链接，我们可以看到如下图所示：
   ![数据格式](https://user-gold-cdn.xitu.io/2017/11/29/16005b6c846eb8d5?w=2552&h=1350&f=png&s=134916)
   从图中我们可以看到，**title**是文章的标题，**summary**是文章的内容，自此我们的数据已经分析完毕。
  
- 定时抓取数据
   - **方式一：**定时数据抓取可以采用crontab或者部署在服务器的方式进行抓取，因为没有阿里云服务器，所以我采用crontab的方式，在Mac下打开console，输入**sudo crontab -e**可以进入编辑定时任务，输入**30 21 * * * /usr/local/bin/python3  /Users/buzheng/work/py/Steven/project/readhub.py**可以看到我指定的是每天早上的21:30分定时执行该脚本。
  - **方式二：**如果你是部署服务器的方式，可以采用Python提供的schedu或者通过While True轮询的方式进行判断，稍后提供的源代码会有涉及。
- 发送数据到邮箱
   我是发送数据到自己的QQ邮箱的，不管是什么邮箱，都需要提供SMTP登录服务，所以需要去到自己的邮箱，开启SMTP服务。
##### 三、效果展示
![效果](https://user-gold-cdn.xitu.io/2017/11/29/16005b6c82ec4ac7?w=2126&h=1234&f=png&s=670316)
##### 四、代码共享
```
#coding=utf-8
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
# 获取指定时间 方式 的数据
def hub_message(start,end,get_type):
    article_messages = ''
    url = 'https://api.readhub.me/wechat/topics?'
    start = start +'000'
    end = end + '999' #没办法 接口如此
    ret = requests.get(url,params={'start':start,'end':end,'type':get_type})
    if ret.status_code == 200:
        article_messages = ret.json()
    return article_messages
# 解析文章
def parse_article(messages):
    messages_list = {}
    total_message = ''
    for article in messages['data']:
        title = '<font color=red><b>'+'★  '+article['title']+'</b></font>' 
        detail = '<br>'+article['summary']+'</br>'
        total_message += title
        total_message += detail
    return total_message
# 发送邮件
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
# 执行定时任务
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
# 结合crontab 定时任务使用这个方法
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
# 函数入口
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    job(0,0) #定时凌晨一分钟查询
    send_with_crontab()
```