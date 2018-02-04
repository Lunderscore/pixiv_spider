# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import os.path
from pixiv_spider.items import PixivSpiderItem
from pixiv_spider.my_config import *

start_url = get_start_url()
cookies = get_cookies()
save_dir = get_save_dir()

 # 常用图片后缀名 因为不登录， 所以只能猜文件后缀
suffix = ["jpg", "png", "jpeg", "gif", "bmp", "none"]
search = "https://www.pixiv.net/search.php"
class PixivSpider(scrapy.Spider):
    name = 'pixiv'
    allowed_domains = ['pixiv.net', 'pximg.net']
    start_urls = [start_url]

    def start_requests(self):
         yield scrapy.Request(url=self.start_urls[0], cookies=cookies)# 这里带着cookie发出请求
    def parse(self, response):
        # 提取图片关键信息
        search_result = response.xpath("//input[@id='js-mount-point-search-result-list']/@data-items")[0].extract()
        # 正则表达式提取出图片 日期 id 信息
        img_pattern = re.compile(r"(?<=img-master\\/)img\\/\d{4}\\/(?:\d{2}\\/){5}\d+")
        count_pattern = re.compile(r"(?<=\"pageCount\":)\d+")
        imgs = img_pattern.findall(search_result)
        counts = count_pattern.findall(search_result)
        for img, count in zip(imgs, counts):
            # 拼接url, 图片默认为.jpg
            imgurl = "https://i.pximg.net/img-original/" + img.replace("\\", "") + "_p0.jpg"
            filename = imgurl[imgurl.rindex("/") + 1:]
            fileid = filename[:filename.index("_")]
            # 如果为1张图片 则不抓取
            if int(count) == 1 and self.has_file(filename[:filename.index(".")]):
                continue
            # 如果大于1张 且存在目录 则不抓取
            elif self.has_file_dir(fileid):
                continue
            yield scrapy.Request(imgurl, self.download_img, meta={"count": count})
        try:
            next_page = response.xpath("//a[@rel='next']/@href")[0].extract()
        except:
            return
        # 下一页
        yield scrapy.Request(search+next_page, self.parse)

    # 下载图片
    def download_img(self, response):
        # 当前图片后缀名
        img_suffix = response.url[response.url.rfind(".") + 1:]
        # 一个图集有多少张图片
        count = int(response.meta["count"])
        # 获取成功返回结果
        if response.status == 200:
            item = PixivSpiderItem()
            item["url"] = response.url
            item["img"] = response.body
            item["count"] = count
            yield item
        # 如果不匹配全部后缀名 则抓取失败
        elif img_suffix == "none":
            logging.error(response.url + "\t\t失败")
            # 如果没有该失败记录 则添加
            with open(save_dir+"/failure.txt", "a+") as f:
                f.seek(0)
                if not response.url+"\n" in f.readlines():
                    f.write(response.url + "\n")
            return
        # 切换后缀名
        else:
            index = suffix.index(img_suffix)
            url = response.url[:response.url.rfind(".") + 1] + suffix[index + 1]
            yield scrapy.Request(url, self.download_img, meta={"count": count})
        # 如果大于1张则继续抓取
        if count != 1:
            for i in range(1, count):
                url = response.url[:response.url.find("_") + 1] + "p" + str(i) + response.url[response.url.rfind("."):]
                yield scrapy.Request(url, self.download_img, meta={"count": count})

    def has_file(self, file_prefix):
            for i in suffix:
                if os.path.exists(save_dir + "/" + file_prefix + "." + i):
                    return True
            else:
                return False
    def has_file_dir(self, fileid):
        return os.path.exists(save_dir + "/" + fileid)
        