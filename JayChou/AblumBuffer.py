#coding=utf-8
class AblumBuffer:
    def __init__(self):
        self.ablum_links = set()
    def add_ablum_link (self,url):
        self.ablum_links.add(url)
    def remove_ablum_link(self,url):
        self.ablum_links.remove(url)