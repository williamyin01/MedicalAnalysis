# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MedicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date= scrapy.Field()
    doctor_id = scrapy.Field()
    question = scrapy.Field()
    answer = scrapy.Field()
    q1 = scrapy.Field()
    a1 = scrapy.Field()
    q2 = scrapy.Field()
    a2 = scrapy.Field()
    q3 = scrapy.Field()
    a3 = scrapy.Field()
    q_id = scrapy.Field()

# advaced q&a item
class QAItem(scrapy.Item):
    id = scrapy.Field()
    date = scrapy.Field()
    doctor_id = scrapy.Field()
    disease = scrapy.Field()
    question = scrapy.Field()
    answer = scrapy.Field()
    q1 = scrapy.Field()
    a1 = scrapy.Field()
    q2 = scrapy.Field()
    a2 = scrapy.Field()
    q3 = scrapy.Field()
    a3 = scrapy.Field()

# doctor item for advanced spider
class DoctorItem(scrapy.Item):
    id = scrapy.Field()
    real_id = scrapy.Field()
    name = scrapy.Field()
    gender = scrapy.Field()
    location = scrapy.Field()
    section_group = scrapy.Field()
    section_group_id = scrapy.Field()
    hospital = scrapy.Field()
    title = scrapy.Field()
