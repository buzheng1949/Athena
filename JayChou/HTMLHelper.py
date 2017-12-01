#coding=utf-8
import requests
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

def main():
    helper = HTMLHelper()
    res = helper.download("http://music.baidu.com/search/album?key=周杰伦")
    print (res)

if __name__ == '__main__':
    main()