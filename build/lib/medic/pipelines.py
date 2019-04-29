# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
from collections import OrderedDict

# class MedicPipeline(object):
#     def process_item(self, item, spider):
#         return item

class Sqlite3Pipeline(object):

    def __init__(self, sqlite_file, sqlite_table):
        self.sqlite_file = sqlite_file
        self.sqlite_table = sqlite_table
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sqlite_file = crawler.settings.get('SQLITE_FILE'), # 从 settings.py 提取
            sqlite_table = crawler.settings.get('SQLITE_TABLE', 'items')
        )

    def open_spider(self, spider):
        self.conn = sqlite3.connect(self.sqlite_file)
        self.cur = self.conn.cursor()
        create_table = '''create table if not exists dxdata (
                date varchar,
                doctor_id int,
                question text,
                answer text,
                q1 text,
                a1 text,
                q2 text,
                a2 text,
                q3 text,
                a3 text,
                q_id int,
                primary key(q_id)
                );'''
        self.cur.execute(create_table)
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        item_clean = OrderedDict({k:v for k,v in item.items() if v })
        insert_sql = "insert into {0}({1}) values ({2});".format(self.sqlite_table, 
                                                                ', '.join(item_clean.keys()),
                                                                ', '.join(['?'] * len(item_clean.keys())))
        try:
            self.cur.execute(insert_sql, tuple(item_clean.values()))
            # self.cur.execute(insert_sql)
            self.conn.commit()
        except sqlite3.Error as er:
            print(er)
        
        return item