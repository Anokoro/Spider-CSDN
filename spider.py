#coding:utf-8
from urllib.request import urlopen
import urllib
import re
from link_finder import LinkFinder
from domain import *
from general import *
headers = {'User-Agent':'Mozilla/57.0.1 (Windows NT 10.0; WOW64) '
                        'Chrome/62.0.3202.94 '}
title_pat = re.compile('(?<=<title>).+?(?=</title>)', re.S)
tag_pat = re.compile('<ul.*?article_tags.*?">.*?(<li><a.*?>(.*?)</a>)*</ul>', re.S)

# 设置Proxy代理
enable_proxy = True
proxy_ip = {"http" : '118.254.142.42:53281'}
proxy_handler = urllib.request.ProxyHandler(proxy_ip)
null_proxy_handler = urllib.request.ProxyHandler({})
if enable_proxy:
    opener = urllib.request.build_opener(proxy_handler)
else:
    opener = urllib.request.build_opener(null_proxy_handler)
urllib.request.install_opener(opener)

class Spider:

    key_word = ''
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    useful_file = ''
    useful_num = 0
    queue = set()
    crawled = set()
    useful = set()

    def __init__(self, project_name, base_url, domain_name, key_word):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.key_word = key_word
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        Spider.useful_file = Spider.project_name + '/useful.txt'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    # 获取种子URL之后，创建对应的文件夹以及结果文件
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    # 填充队列，更新文件
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:  # 当前页尚未被抓取
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))  # 从当前网页中爬取新的URL并加到queue中

            Spider.queue.remove(page_url)  # 从queue集合中删除该已被爬取的URL
            Spider.crawled.add(page_url)   # 将该已被爬取的URL加入crawled集合中
            Spider.update_files()          # 更新文件

    # 下载并读取html内容 and 检查html文档的合法性
    # and 返回当前网页找到的URL的集合
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            rep = urllib.request.Request(page_url,headers=headers)
            response = urlopen(rep, timeout=3)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("UTF-8")
            finder = LinkFinder(Spider.base_url, page_url)  # 定义LinkFinder
            finder.feed(html_string)  # 调用handle_starttag()解析下载的HTML文档,找到所有的URL
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()  # 返回当前爬取的网页中找到的URL集合

    # 对gather_links得到的URL进行过滤，并加到queue集合中
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue  # 排除已经在已抓取和待抓取集合中的
            if Spider.domain_name != get_domain_name(url):
                continue  # 排除和种子URL的domain name不同的
            Spider.queue.add(url)  # 往待抓取集合中加入新的内容
            try:
                text = urlopen(url).read().decode("utf-8")
                title = re.findall(title_pat, text)  # 得到文档的title
                tags = re.findall(tag_pat,text)  # 找到文章的标签（如果有的话）

                if Spider.key_word in title[0] or text.count(Spider.key_word) > 5:
                    Spider.useful.add(url)  # 如果在文章的title中包含要查询的关键字，
                                            # 或者虽然title中不包含，但主体部分出现超过5次，则加入到useful集合
                    Spider.useful_num += 1
                    print("Find an useful page, total:%d url = %s" %(Spider.useful_num, url))
                for item in tags:
                    if Spider.key_word in item:
                        Spider.useful.add(url)  # 如果在文章的标签中包含要查询的关键字，则加入到useful集合
                        Spider.useful_num += 1
                        print("Find an useful page, total:%d url = %s" % (Spider.useful_num, url))

            except Exception as e:
                continue

    # 更新文件
    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
        set_to_file(Spider.useful, Spider.useful_file)