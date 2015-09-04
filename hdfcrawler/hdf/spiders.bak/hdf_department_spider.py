# # -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.link import Link

from hdf.hdf_items import DepartmentItem, HospitalItem

import urlparse
import json
import chardet
import re



class OnsiteDoctorSpider(BaseSpider):
    name = "hdf_department"
    allowed_domains = ["haodf.com"]
#    url_root = "http://www.haodf.com" # for href join
    start_urls = [
        "http://www.haodf.com/yiyuan/all/list.htm",
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
        
#        hospital_url = 'http://www.haodf.com/hospital/DE4roiYGYZwXhYmS30yF9V0wc.htm'
#        request = Request(hospital_url, callback=self.parse_hospital)
#        request.meta['city'] = u'上海'
#        request.meta['area'] = u'徐汇'
#        request.meta['grade'] = u'三甲'
#        request.meta['feature'] = u'综合'
#        yield request
#        return
           
            
        hxs = HtmlXPathSelector(response)
        # Request for different city
        for city_url in hxs.select("//div[@id='el_tree_1000000']/div[@class='kstl']/a/@href").extract():
            yield Request(city_url, callback=self.parse) 
        
        city = hxs.select('//div[@class="kstl2"]/a/text()')[0].extract()
        
        hospital_url_list = hxs.select("//div[@class='m_ctt_green']/ul/li")
        for hospital_url in hospital_url_list:
            hospital_name = hospital_url.select('a/text()')[0].extract()
            hospital_relative_url = hospital_url.select('a/@href')[0].extract()
            base_url = get_base_url(response)
            hospital_absolute_url = urlparse.urljoin(base_url, hospital_relative_url)
            request = Request(hospital_absolute_url, callback= self.parse_hospital)
            request.meta['city'] = city
            request.meta['area'] = hospital_url.select('parent::*/parent::*/preceding-sibling::*[1]/text()')[0].extract()
            match_group = re.search(u'\((?P<grade>\S+)(|, 特色:(?P<feature>\S+))\)', hospital_url.select('span/text()')[0].extract())

            request.meta['hospital_name'] = hospital_name
            if match_group:
                if match_group.group('grade'):
                    request.meta['grade'] = match_group.group('grade')
                if match_group.group('feature'):
                    request.meta['feature'] = match_group.group('feature')
            yield request

        
    def parse_hospital(self, response):
        hxs = HtmlXPathSelector(response)
        item = DepartmentItem()
        item['hospital_id'] = re.search('hospital/(?P<hospital_id>[^.]*)\.htm', response.url).group('hospital_id')
        hospital_about_selector = hxs.select("//table[@id='hosabout']")
        about_re = re.compile(u'.*?地　　址：</nobr>(?P<address>[^<]*)<.*?电　　话：</nobr>(?P<phone>[^<]*)<.*', re.S)
        match_group = about_re.search(hospital_about_selector[0].extract())
        
        department_list = hxs.select("//a[contains(@href, 'http://www.haodf.com/faculty')]")
        for department in department_list:

            item['department_name'] = department.select('text()')[0].extract()
            item['department_category'] = department.select('parent::*/parent::*/parent::*/parent::*/preceding-sibling::*[1]/text()')[0].extract()
            if match_group: 
                if match_group.group('address'):
                   item['address'] = match_group.group('address') 
                if match_group.group('phone'):
                    item['phone'] = re.sub(u"(—|－)", "-", match_group.group('phone'))
            if response.meta.get('hospital_name', None):
                item['hospital_name'] = response.meta['hospital_name']
            if response.meta.get('grade', None):
                item['grade'] = response.meta['grade']
            if response.meta.get('feature', None):
                item['feature'] = response.meta['feature']
            if response.meta.get('city', None):
                item['city'] = response.meta['city']
            if response.meta.get('area', None):
                item['area'] = response.meta['area']
            yield item



    


