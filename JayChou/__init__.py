#coding=utf-8
import requests
from bs4 import BeautifulSoup
headers = {
    'Referer':'http://music.163.com/',
    'Host':'music.163.com',
    'Host':'music.163.com',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
}
play_url = 'http://music.163.com/playlist?id=317113395'
s = requests.session()
s = BeautifulSoup(s.get(play_url,headers = headers).content)
main = s.find('ul',{'class':'f-hide'})
for music in main.find_all('a'):
    print music.text