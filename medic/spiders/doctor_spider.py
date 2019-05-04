# encoding=utf-8
import scrapy
from scrapy.loader import ItemLoader
import json
from urllib.parse import urlencode
from medic.items import *

# scrape doctors from each section json
# then scrape lists of questions answered by each doctor
# then scrape dialogs of questions
class DoctorSpider(scrapy.Spider):
    name = 'doctorSpider'
    allow_domains = ['dxy.com']
    custom_settings = {
        # 'FEED_URI': 'dxadv-doctor.csv',
        # 'FEED_IMPORT': 'CSV',
        'SQLITE_FILE': 'dxadv.db',
        'SQLITE_TABLE': 'doctors',
        'ITEM_PIPELINES': {
            'medic.pipelines.DxAdvPipeline': 300,
        },
    }

    def start_requests(self):
        section_group_ids= [9,2,5,8,40,3,60,12,64,57,18,98,6,58,11,10,4,73,71,56,55,7,66,63,65,76,70,394,68,79,]
        # section_group_ids = [9]
        for sg_id in section_group_ids:
            for page_index in range(1, 18):
                secton_param = {
                    'rank_type': 0,
                    'area_type': 0,
                    'page_index': page_index,
                    'items_per_page':20,
                    'section_group_id': sg_id,
                    'ad_status':1
                }
                url = 'https://ask.dxy.com/view/i/sectiongroup/member?' + urlencode(secton_param)
                yield scrapy.Request(url, meta={'sg_id': sg_id, 'nitems': 20}, callback=self.parse)
    def parse(self, response):
        jsonresponse = json.loads(response.body)
        sg_id = response.meta['sg_id']
        for i in range(response.meta['nitems']):
            # il = scrapy.loader.ItemLoader(item=DoctorItem(), response=response)
            it = DoctorItem()
            doctor_json = jsonresponse['data']['items'][i]
            doctor_id = doctor_json['id']
            real_id = doctor_json['doctor']['id']
            name = doctor_json['doctor']['nickname']
            gender = doctor_json['doctor']['sex']
            location = doctor_json['doctor']['location_name']
            sec_name = doctor_json['doctor']['section_name']
            hospital = doctor_json['doctor']['hospital_name']
            title = doctor_json['doctor']['job_title_name']
            it['id'] = doctor_id
            it['real_id'] = real_id
            it['name'] = name
            it['gender'] = gender
            it['location'] = location
            it['section_group'] = sec_name
            it['section_group_id'] = sg_id
            it['hospital'] = hospital
            it['title'] = title
            yield it
