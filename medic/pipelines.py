# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
from collections import OrderedDict

class DxAdvPipeline(object):

    def __init__(self, sqlite_file, sqlite_table):
        self.sqlite_file = sqlite_file
        self.sqlite_table = sqlite_table
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sqlite_file = crawler.settings.get('SQLITE_FILE'), 
            sqlite_table = crawler.settings.get('SQLITE_TABLE', 'items')
        )

    def open_spider(self, spider):
        self.conn = sqlite3.connect(self.sqlite_file)
        self.cur = self.conn.cursor()
        create_table = '''create table if not exists dialogs (
                id int not null,
                date varchar,
                doctor_id int,
                question text,
                answer text,
                q1 text,
                a1 text,
                q2 text,
                a2 text,
                primary key(id)
                );'''
        self.cur.execute(create_table)
        create_table = '''create table if not exists doctors (
                id int not null,
                real_id int,
                name int not null,
                gender bit,
                location name,
                section_group varchar,
                section_group_id int,
                hospital varchar,
                title varchar,
                primary key(id)
                );'''
        self.cur.execute(create_table)
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        if spider.name == 'dxspider':
            update_sql = 'update {0} set {1} where id={2}'.format(self.sqlite_table,
                                                                    ','.join(['{}=?'.format(key) for key in item]),
                                                                       item['id'] )
            self.cur.execute(update_sql, tuple(item.values()))
        else:
            insert_sql = "insert into {0}({1}) values ({2});".format(self.sqlite_table, 
                                                                    ', '.join(item.keys()),
                                                                    ', '.join(['?'] * len(item.keys())))
            self.cur.execute(insert_sql, tuple(item.values()))
        return item