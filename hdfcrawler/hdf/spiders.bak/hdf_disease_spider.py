# # -*- coding: utf-8 -*-

from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.link import Link
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from hdf.hdf_items import DiseaseItem
import urlparse
import json
import chardet
import re

import time

class OnsiteDoctorSpider(BaseSpider):
    name = "hdf_disease"
    allowed_domains = ["haodf.com"]
#    url_root = "http://www.haodf.com" # for href join
    start_urls = [
        "http://www.haodf.com/jibing/list.htm",
#        "http://www.haodf.com/jibing/nanke/list.htm",
    ]
    
    # rules = (
    #     # Extract links matching 'category.php' (but not matching 'subsection.php')
    #     # and follow links from them (since no callback means follow=True by default).
    #     Rule(SgmlLinkExtractor(allow=(r'http://www.haodf.com/yiyuan/\w+/list.htm', )), follow=True, callback='parse_item'),

    #     # Extract links matching 'item.php' and parse them with the spider's method parse_item
    #     #Rule(SgmlLinkExtractor(allow=('item\.php', )), callback='parse_item'),
    # )
    
    #parse hospitals
    def parse(self, response):
        
#        category_url = 'http://www.haodf.com/jibing/laonianbingneike/list.htm'
#        category_url = "http://www.haodf.com/jibing/xiaohuaneike/list.htm"
#        category_url = "http://www.haodf.com/jibing/nanke/list.htm"
#        request = Request(category_url, callback=self.parse_category_1)
#        yield request
#        return 
            
        hxs = HtmlXPathSelector(response)
        for category_0_url in hxs.select('//div[@class="kstl"]/a/@href').extract():
            yield Request(urlparse.urljoin(response.url, category_0_url.strip()), 
                callback=self.parse)

        category_1_selector = hxs.select('//div[@class="ksbd"]/ul/li/a/@href')
        if len(category_1_selector) == 0:
            category_0 = None
            url_match = self.re_url.search(response.url)
            if url_match:
                relative_url = url_match.group("relative_url")
                kstl_selector = hxs.select('//div[@class="kstl"]/a[@href="%s"]/text()' % relative_url)
                #kstl_selector = hxs.select('//div[@class="kstl"]/a[contains(@href,"%s")]/text()' % relative_url)
                if len(kstl_selector) == 1:
                    category_0 = kstl_selector[0].extract()

            disease_selector = hxs.select(
                "//div[@class='m_box_green']//div[@class='ct']//a")
            for disease in disease_selector:
                item = DiseaseItem()
                item['disease_name'] = disease.select('text()')[0].extract()
                disease_id_selector = disease.select('@href')
                if len(disease_id_selector) == 1:
                    disease_id_group = self.disease_id_re_obj.search(
                        disease_id_selector[0].extract())
                    if disease_id_group != None:
                        item['disease_id'] = disease_id_group.group("disease_id")

                category_2_selector = disease.select(
                    'parent::li/parent::ul/parent::div/preceding-sibling::div[1]/'
                    'text()')
                if len(category_2_selector) == 1:
                    item['category_2'] = category_2_selector[0].extract()
                
                description_selector = disease.select('following-sibling::text()')
                if len(description_selector) == 1:
                    num_match_group = self.re_obj.search(
                        description_selector[0].extract())
                    if num_match_group != None:
                        item['hdf_doctor_recommend_number'] = num_match_group.group(
                            'num_recommend')
                        item['hdf_doctor_online_number'] = num_match_group.group(
                            'num_online')
                if category_0:
                    item['category_0'] = category_0
                yield item
        else:
            for category_1_url in category_1_selector.extract():
                yield Request(urlparse.urljoin(response.url, category_1_url.strip()), 
                    callback=self.parse_category_1)

    re_url = re.compile(u'(?P<relative_url>/jibing/[^/]*/list\.htm)')
    re_obj = re.compile(
        u'\((?P<num_recommend>\d*)位推荐大夫,(?P<num_online>\d*)位提供在线咨询\)')
    disease_id_re_obj = re.compile(
        u'/[^/]*/(?P<disease_id>[^\.]*)\.htm')

    def parse_category_1(self, response):
        hxs = HtmlXPathSelector(response)

        category_0 =None
        category_0_selector = hxs.select(
            '//div[@class="ksbd"]/preceding-sibling::div[1]/a/text()')
        if len(category_0_selector) == 1:
            category_0 = category_0_selector[0].extract()

        category_1 = None
        category_1_selector = hxs.select('//li[@class="item"]/a/text()')
        if len(category_1_selector) == 1:
            category_1 = category_1_selector[0].extract()

        disease_selector = hxs.select(
            "//div[@class='m_box_green']//div[@class='ct']//a")
        for disease in disease_selector:
            item = DiseaseItem()
            item['disease_name'] = disease.select('text()')[0].extract()
            disease_id_selector = disease.select('@href')
            if len(disease_id_selector) == 1:
                disease_id_group = self.disease_id_re_obj.search(
                    disease_id_selector[0].extract())
                if disease_id_group != None:
                    item['disease_id'] = disease_id_group.group("disease_id")

            category_2_selector = disease.select(
                'parent::li/parent::ul/parent::div/preceding-sibling::div[1]/'
                'text()')
            if len(category_2_selector) == 1:
                item['category_2'] = category_2_selector[0].extract()
            
            description_selector = disease.select('following-sibling::text()')
            if len(description_selector) == 1:
                num_match_group = self.re_obj.search(
                    description_selector[0].extract())
                if num_match_group != None:
                    item['hdf_doctor_recommend_number'] = num_match_group.group(
                        'num_recommend')
                    item['hdf_doctor_online_number'] = num_match_group.group(
                        'num_online')
            if category_0:
                item['category_0'] = category_0
            if category_1:
                item['category_1'] = category_1
            yield item

