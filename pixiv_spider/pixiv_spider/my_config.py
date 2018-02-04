import re


cookies = ""
# 保存当前目录下文件夹名
save_dir = "東方Project10000users入り"
# 开始url
params = "?s_mode=s_tag_full&word=%E6%9D%B1%E6%96%B9Project10000users%E5%85%A5%E3%82%8A"
start_url = "https://www.pixiv.net/search.php" + params


def get_start_url():
    return start_url

def get_save_dir():
    return save_dir

def get_cookies():
    if not cookies:
        return {}
    cookie_list = re.split("[;\s]+", cookies)
    cookie_dict = {}
    for i in cookie_list:
        t = i.split("=")
        cookie_dict.update({t[0]: t[1]})
    return cookie_dict