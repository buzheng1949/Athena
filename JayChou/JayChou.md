**心血来潮想给我家杰伦做张云图头像，于是就有了下面的事情，事情发生在昨天晚上的12点**

[给杰伦做张头像源码](https://github.com/buzheng1949/Athena)

如果链接无法点击，请直接点击：https://github.com/buzheng1949/Athena

[自动化脚本登录服务器](https://github.com/buzheng1949/Athena/tree/master/FreeServer)

- 需求分析

  - 需要的数据从哪里来？
    - 酷狗
    - 网易云
    - QQ音乐
   
  后续可能会进行评论的抓取，于是选择了网易云
  - 如何抓取
    - 可以先抓专辑数据、再从专辑数据抓歌曲数据、再从歌曲数据抓歌曲的歌词
  - 如何生成热词分析
    - 我们采用Wordcloud词云进行歌词切词以及分析
  - 定下我们需要的第三方库
    - 网络请求我们需要用requests，requests可能会有中文乱码的坑，如果遇到问题可以使用urlib
   - 词频切词以及热词图生成需要用matplotlib、wordcloud、jieba、PIL
- 动手做起来
 - 首先我们需要看一下怎么获取专辑的歌曲呢？
  ![获取所有专辑接口](https://user-gold-cdn.xitu.io/2017/12/1/1601139faac32104?w=2560&h=1312&f=png&s=852127)
  从上图我们可以看出，网易云音乐的专辑页面的请求地址是**http://music.163.com/artist/album?id=6452&limit=100**id指的是某个艺人的代号？limit是获取的专辑最大数量，offset是从第几张开始获取。
  
  既然可以获取到专辑，我们可以审查网页元素，看看我们需要的专辑链接可以在哪里获得？
  ![单张专辑链接获取](https://user-gold-cdn.xitu.io/2017/12/1/1601139fa154633c?w=2560&h=1218&f=png&s=1130041)
  从图我们可以看到，红框里面就是我们需要的href每个专辑的链接，需要注意的是，这里是短链接，我们需要在链接前面加入**http://music.163.com/**拼接成完整的链接。
  
  ```
  # 获取所有专辑的链接
    def get_all_ablum_links(self,url):
        ablum_message = self.downloader.download(url)
        if ablum_message is None:
            print ("get the ablum's detail image")
            return 
        else:
            soup = BeautifulSoup(ablum_message,'html.parser',from_encoding='utf-8')
            ablum_nodes = soup.find_all('div',class_ ='u-cover u-cover-alb3')
            for node in ablum_nodes:
                ablum_link_short = node.find('a').get('href').encode('utf-8')
                ablum_link = 'http://music.163.com'+ablum_link_short
                self.urls.add(ablum_link)
  
  ```
  
 - 从上面我们可以获取所有专辑的具体链接，现在我们来看下单张专辑的歌曲链接，如下图所示：
  ![](https://user-gold-cdn.xitu.io/2017/12/1/1601139fa3e9be9a?w=2534&h=1356&f=png&s=818942)
  从图中我们可以看到，href属性里面带着歌曲的信息，这是我们要的歌曲ID.
  
  ```
  # 获取所有的歌曲的ID以及歌曲名存放在字典里面
    def get_all_songs(self,ablum_links):
        while len(self.urls) > 0:
            ablum_url = self.urls.pop()
            ablum_songs_detail = self.downloader.download(ablum_url)
            soup = BeautifulSoup(ablum_songs_detail,'html.parser',from_encoding='utf-8')
            nodes = soup.findAll(name = 'a', attrs = {'href':re.compile(r'/song.id=\d{1,10}')})
            for node in nodes:
                song_short_link = node.get('href')
                song_id = re.findall("\d+",song_short_link)[0]
                self.songs_dict[node.get_text()] = song_id
        return self.songs_dict
  ```
  
 -  我们可以拿到歌曲的ID，我们也可以获取歌曲的具体歌词了,接口如下图所示：**http://music.163.com/api/song/lyric?lv=1&kv=1&tv=-1&id=186039**其中ID就是上一步我们获取的歌曲ID
 ![歌曲歌词](https://user-gold-cdn.xitu.io/2017/12/1/1601139fa12806e3?w=2560&h=1272&f=png&s=709497)
 可以看到歌词了，再来一个正则匹配，我们就可以获取我们要的歌词信息了
 
 ```
 # 通过歌曲ID获取歌曲的歌词
    def get_lyric_by_music_id(self,song_id):
        lrc_url = 'http://music.163.com/api/song/lyric?' + 'id=' + str(song_id) + '&lv=1&kv=1&tv=-1'
        lyric = requests.get(lrc_url) 
        j = json.loads(lyric.text)
        try:
            lrc = j['lrc']['lyric']
            pat = re.compile(r'\[.*\]')
            lrc = re.sub(pat,"",lrc)
            lrc = lrc.strip()
            return lrc
        except:
            print ('cannot get the lrc from Net,it is has no matter')
 ```
 
 - 获取完歌词，下一步是对歌词进行切词，整理出高频词汇，这个步骤我们采用jieba进行分析,使用方式非常简单，就是调用jieba的cut方法即可。
 
 ```
 # 分词后进行数据采集并生成热词云图
    def get_hot_words (self,songs_dict):
            for key in songs_dict.keys():
                try:
                    song_id = self.songs_dict.get(key)
                    song_detail = self.get_lyric_by_music_id(song_id).encode('utf-8')
                    self.lyrics += song_detail
                except:
                    # 有些歌曲是木有歌词的我们可以忽略
                    print ('the song has no lrc ,the song id is %s'%(song_id))
            words=list(jieba.cut(self.lyrics)) # 把所有歌词进行分词
            key_words = []
            for word in words:
                try:
                    if len(word)>1:
                        key_words.append(word)
                except :
                    pass
            hot_key_words=r' '.join(key_words)
            return hot_key_words

 ```
 
 - 使用jieba进行高频词汇分析后，我们可以使用wordcloud加PIL进行图片生成。需要注意的是，我们是需要指定字体的，于是我下载了mysh使用，没有指定字体会一堆乱码的现象。
 
 ```
 # 生成热词云图
    def assemble_hot_image(self,hot_key_words):
            path='font/msyh.ttf'
            path=unicode(path, 'utf8').encode('utf-8')
            alice_mask = np.array(PIL.Image.open('images/jay.jpeg'))
            wordcloud = WordCloud(font_path=path, 
                                background_color="white",   
                                 width=1800,
                                 height=800,
                                 mask=alice_mask,
                                 max_words=3000,
                                 max_font_size=12,
                                 random_state=32) 
            wordcloud = wordcloud.generate(hot_key_words)
            wordcloud.to_file('images/image.jpg')
            plt.imshow(wordcloud)
            plt.axis("off")
            plt.show()
 ```
- 看看效果吧，嘿嘿，我使用了一张杰伦的经典头像作为背景图，生成的云图如下：
 ![Jay头像](https://user-gold-cdn.xitu.io/2017/12/1/1601139faabf8b28?w=301&h=458&f=jpeg&s=5909)
 ![云图](https://user-gold-cdn.xitu.io/2017/12/1/1601139fab358926?w=301&h=458&f=jpeg&s=25001)
 至此我们的工作也就完工了。
 
- 依旧不出意外的源码分享

```
# coding=utf-8
import requests
from bs4 import BeautifulSoup
import sys
import chardet
import re
import json
from wordcloud import WordCloud
import jieba
import PIL
import matplotlib.pyplot as plt
import jieba.analyse
import numpy as np
import os

# 下载网页工具类
class HTMLHelper:
    def __init__(self):
        pass
    def download(self,url):
        s = requests.session()
        headers = {
        'Referer':'http://music.163.com/',
        'Host':'music.163.com',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
        }
        ret = s.get(url,headers = headers)
        if ret.status_code == 200:
            return ret.text
        else:
            return None

# 爬虫工具类
class Spider:
    def __init__(self):
        self.urls = set()
        self.downloader = HTMLHelper()
        self.songs_dict = {}
        self.lyrics= ''

    # 生成热词图
    def image_for_jaychou(self,url):
        ablums = self.get_all_ablum_links(url)
        songs_dict = self.get_all_songs(ablums)
        hot_key_words = self.get_hot_words(songs_dict)
        self.assemble_hot_image(hot_key_words)

    # 获取所有专辑的链接
    def get_all_ablum_links(self,url):
        ablum_message = self.downloader.download(url)
        if ablum_message is None:
            print ("get the ablum's detail image")
            return 
        else:
            soup = BeautifulSoup(ablum_message,'html.parser',from_encoding='utf-8')
            ablum_nodes = soup.find_all('div',class_ ='u-cover u-cover-alb3')
            for node in ablum_nodes:
                ablum_link_short = node.find('a').get('href').encode('utf-8')
                ablum_link = 'http://music.163.com'+ablum_link_short
                self.urls.add(ablum_link)
    
    # 获取所有的歌曲的ID以及歌曲名存放在字典里面
    def get_all_songs(self,ablum_links):
        while len(self.urls) > 0:
            ablum_url = self.urls.pop()
            ablum_songs_detail = self.downloader.download(ablum_url)
            soup = BeautifulSoup(ablum_songs_detail,'html.parser',from_encoding='utf-8')
            nodes = soup.findAll(name = 'a', attrs = {'href':re.compile(r'/song.id=\d{1,10}')})
            for node in nodes:
                song_short_link = node.get('href')
                song_id = re.findall("\d+",song_short_link)[0]
                self.songs_dict[node.get_text()] = song_id
        return self.songs_dict

    # 通过歌曲ID获取歌曲的歌词
    def get_lyric_by_music_id(self,song_id):
        lrc_url = 'http://music.163.com/api/song/lyric?' + 'id=' + str(song_id) + '&lv=1&kv=1&tv=-1'
        lyric = requests.get(lrc_url) 
        j = json.loads(lyric.text)
        try:
            lrc = j['lrc']['lyric']
            pat = re.compile(r'\[.*\]')
            lrc = re.sub(pat,"",lrc)
            lrc = lrc.strip()
            return lrc
        except:
            print ('cannot get the lrc from Net,it is has no matter')

    # 分词后进行数据采集并生成热词云图
    def get_hot_words (self,songs_dict):
            for key in songs_dict.keys():
                try:
                    song_id = self.songs_dict.get(key)
                    song_detail = self.get_lyric_by_music_id(song_id).encode('utf-8')
                    self.lyrics += song_detail
                except:
                    # 有些歌曲是木有歌词的我们可以忽略
                    print ('the song has no lrc ,the song id is %s'%(song_id))
            words=list(jieba.cut(self.lyrics)) # 把所有歌词进行分词
            key_words = []
            for word in words:
                try:
                    if len(word)>1:
                        key_words.append(word)
                except :
                    pass
            hot_key_words=r' '.join(key_words)
            return hot_key_words

    # 生成热词云图
    def assemble_hot_image(self,hot_key_words):
            path='font/msyh.ttf'
            path=unicode(path, 'utf8').encode('utf-8')
            alice_mask = np.array(PIL.Image.open('images/jay.jpeg'))
            wordcloud = WordCloud(font_path=path, 
                                background_color="white",   
                                 width=1800,
                                 height=800,
                                 mask=alice_mask,
                                 max_words=3000,
                                 max_font_size=12,
                                 random_state=32) 
            wordcloud = wordcloud.generate(hot_key_words)
            wordcloud.to_file('images/image.jpg')
            plt.imshow(wordcloud)
            plt.axis("off")
            plt.show()

    

def main():
    spider = Spider()
    url = "http://music.163.com/artist/album?id=6452&limit=100"
    spider.image_for_jaychou(url)

if __name__ == '__main__':
    main()
```
 
 
 
 
  