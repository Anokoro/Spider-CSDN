from urllib.parse import urlparse


# 获取域名 (baidu.com)
def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')
        return results[-2] + '.' + results[-1]
    except:
        return ''


# 获取域名-sub (www.baidu.com)
def get_sub_domain_name(url):
    try:
        return urlparse(url).netloc
    except:
        return ''