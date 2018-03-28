from html.parser import HTMLParser
from urllib import parse


class LinkFinder(HTMLParser):

    def __init__(self, base_url, page_url):
        super().__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.links = set()

    # 覆盖starttag方法,可以进行一些自定义操作，调用feed()的时候执行此函数
    def handle_starttag(self, tag, attrs):
        if tag == 'a':  # 找到a标签
            for (attribute, value) in attrs:
                if attribute == 'href':  # 找到a标签的href的属性，得到其值
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url)

    def page_links(self):
        return self.links

    def error(self, message):
        pass  # pass 不做任何事情，一般用做占位语句。
