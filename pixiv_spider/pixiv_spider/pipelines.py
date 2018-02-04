# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os.path
import logging
import sys
from pixiv_spider.my_config import *


# 文件夹名
save_dir = get_save_dir()

if not os.path.exists(save_dir):
    os.mkdir(save_dir)

class PixivSpiderPipeline(object):
    def open_spider(self, spider):
        self.f = open("{}/{}.txt".format(save_dir, save_dir), "a+")
        self.f.seek(0)
        self.url_list = self.f.readlines()
    def process_item(self, item, spider):
        filename = item["url"][item["url"].rfind("/")+1:]
        # 一张图片时
        if int(item["count"]) == 1:
            filepath = "{}/{}".format(save_dir, filename)
        # 多张图片时
        else:
            filedir = filename[:filename.index("_")]
            if not os.path.exists(save_dir + "/" + filedir):
                os.mkdir(save_dir + "/" + filedir)
            filepath = "{}/{}/{}".format(save_dir, filedir, filename)
        # 如果不存在该信息 则保存
        if not item["url"] + "\n" in self.url_list:
            self.f.write(item["url"] + "\n")
            self.url_list.append(item["url"] + "\n")
        # 保存图片
        with open(filepath, "wb") as ff:
            ff.write(item["img"])
            logging.info(filename + "\t处理成功")
        return item
    def close_sipder(self, spider):
        self.f.close()