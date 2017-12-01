# coding=utf-8
import requests
from HTMLHelper import HTMLHelper
from bs4 import BeautifulSoup
import sys
import chardet
from AblumBuffer import AblumBuffer
import re
import json
from wordcloud import WordCloud
import jieba
import PIL
import matplotlib.pyplot as plt
import jieba.analyse
import numpy as np
import os

# 爬虫工具类
class Spider:
    def __init__(self):
        self.urls = AblumBuffer()
        self.downloader = HTMLHelper()
        self.song_urls = {}
        self.lyrics= ''

    def wordcloudplot(self,txt):
            path='/Users/buzheng/github/Athena/JayChou/font/msyh.ttf'
            path=unicode(path, 'utf8').encode('utf-8')
            alice_mask = np.array(PIL.Image.open('jay.jpeg'))
            wordcloud = WordCloud(font_path=path, 
                                background_color="white",   
                                 width=1800,
                                 height=800,
                                 mask=alice_mask,
                                 max_words=3000,
                                 max_font_size=12,
                                 random_state=32) 
            wordcloud = wordcloud.generate(txt)
            wordcloud.to_file('image.jpg')
            plt.imshow(wordcloud)
            plt.axis("off")
            plt.show()

    # 获取所有专辑的链接
    def get_all_ablum_links(self,url):
        ablum_message = self.downloader.download(url)
        if ablum_message is None:
            print ("获取专辑数据失败")
            return 
        else:
            soup = BeautifulSoup(ablum_message,'html.parser',from_encoding='utf-8')
            ablum_nodes = soup.find_all('div',class_ ='u-cover u-cover-alb3')
            for node in ablum_nodes:
                ablum_link_short = node.find('a').get('href').encode('utf-8')
                ablum_link = 'http://music.163.com'+ablum_link_short
                self.urls.add_ablum_link(ablum_link)
    def get_all_songs(self,ablum_links):
        while len(self.urls.ablum_links) > 0:
            ablum_url = self.urls.ablum_links.pop()
            ablum_songs_detail = self.downloader.download(ablum_url)
            soup = BeautifulSoup(ablum_songs_detail,'html.parser',from_encoding='utf-8')
            nodes = soup.findAll(name = 'a', attrs = {'href':re.compile(r'/song.id=\d{1,10}')})
            for node in nodes:
                song_short_link = node.get('href')
                song_id = re.findall("\d+",song_short_link)[0]
                self.song_urls[node.get_text()] = song_id
        return self.song_urls

    def get_lyric_by_music_id(self,music_id):#通过音乐的id得到歌词
        lrc_url = 'http://music.163.com/api/song/lyric?' + 'id=' + str(music_id) + '&lv=1&kv=1&tv=-1'
        lyric = requests.get(lrc_url)
        json_obj = lyric.text
        j = json.loads(json_obj)
        try:
            lrc = j['lrc']['lyric']
            pat = re.compile(r'\[.*\]')
            lrc = re.sub(pat,"",lrc)
            lrc = lrc.strip()
            return lrc
        except KeyError as e:
            pass

    def assemble_lrc_txt (self,song_urls):
            for key in song_urls.keys():
                try:
                    song_id = self.song_urls.get(key)
                    song_detail = self.get_lyric_by_music_id(song_id).encode('utf-8')
                    self.lyrics += song_detail
                except:
                    pass
            words=list(jieba.cut(self.lyrics))
            a = []
            for word in words:
                try:
                    if len(word)>1:
                        a.append(word)
                except :
                    pass
            txt=r' '.join(a)
            self.wordcloudplot(txt)

    def assemble_hot_image(self):
        for filename in os.listdir('lrc'):
            with open('lrc' + '/' + filename,'r') as f:
                message = f.read().decode('utf-8')
                self.lyrics += message.replace(' ','')
        words=list(jieba.cut(self.lyrics))
        a = []
        for word in words:
            try:
                if len(word)>1:
                    a.append(word)
            except :
                print ('exccc')
                pass
        txt=r' '.join(a)
        print txt

        
      

        

def main():
    # reload(sys)
    # sys.setdefaultencoding('utf-8')
    spider = Spider()
    ablums = spider.get_all_ablum_links("http://music.163.com/artist/album?id=6452&limit=100")
    song_urls = spider.get_all_songs(ablums)
    spider.assemble_lrc_txt(song_urls)
    # spider.assemble_hot_image()

if __name__ == '__main__':
    main()