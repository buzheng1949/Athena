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