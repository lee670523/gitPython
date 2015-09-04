# # -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.link import Link

from hdf.items import CityItem, HospitalItem, DoctorItem
from hdf.doctor_items import DoctorDetailItem

import urlparse
import json
import chardet
import re


import codecs
f = codecs.open('/home/albert/projects/crawl/kkhtools/hdfcrawler/hdf/test/a.html', encoding='utf-8', mode='a+')


class OnsiteDoctorSpider(BaseSpider):
    name = "schedule2"
#    allowed_domains = ["haodf.com"]
    allowed_domains = ["haodf.com"]
#    url_root = "http://www.haodf.com" # for href join
    start_urls = [
        "http://www.haodf.com/yiyuan/all/list.htm",
#        "http://www.haodf.com/yiyuan/shanghai/list.htm",
#        "http://www.haodf.com/doctor/DE4r0BCkuHzduCUWCUsPGYy9dgccG.htm#",
#        "http://www.haodf.com/doctor/DE4r0BCkuHzduCUWCUsPGYy9dgccG.htm#",
#        "http://www.haodf.com/doctor/DE4r08xQdKSLBfNvQgzM21bXlzuR.htm#",
#        "http://www.haodf.com/doctor/DE4r0BCkuHzduCUWCUsPGYy9dgccG.htm#",
    ]
    
    #for time fetch
    weekday_dict = {1: u'星期一', 
               2: u'星期二',
               3: u'星期三',
               4: u'星期四',
               5: u'星期五',
               6: u'星期六',
               7: u'星期日'}
    
    day_part_dict = {1: u'上午',
                2: u'下午',
                3: u'夜间'}
    # rules = (
    #     # Extract links matching 'category.php' (but not matching 'subsection.php')
    #     # and follow links from them (since no callback means follow=True by default).
    #     Rule(SgmlLinkExtractor(allow=(r'http://www.haodf.com/yiyuan/\w+/list.htm', )), follow=True, callback='parse_item'),

    #     # Extract links matching 'item.php' and parse them with the spider's method parse_item
    #     #Rule(SgmlLinkExtractor(allow=('item\.php', )), callback='parse_item'),
    # )
    
    #parse hospitals
    def parse(self, response):
#        doctor_url = "http://www.haodf.com/doctor/DE4r0eJWGqZNwLDLFGUsmUYX-4THvahP.htm" #no truncate
#        doctor_url = "http://www.haodf.com/doctor/DE4r0eJWGqZNwLDkVZU50nyZYjeZpcO4.htm" # have comment in bio
#        doctor_url = "http://www.haodf.com/doctor/DE4r08xQdKSLFhU0itdX6gWDmEzh.htm" # bio 暂无
#        doctor_url = "http://www.haodf.com/doctor/DE4r08xQdKSLVwXJ5vKSvlgzgq2c.htm" # bio contains <a>
#        doctor_url = "http://www.haodf.com/doctor/DE4r0BCkuHzduGIz8Zqr5q33q1fJD.htm" #bio in td must be with <br> end； 页面自己显示也不正确
#        doctor_url = "http://www.haodf.com/doctor/DE4r0BCkuHzduSNxaYRwE-9BS0ak-.htm" #尖括号中内容无显示
#        doctor_url = "http://www.haodf.com/doctor/DE4r08xQdKSLBfLu-dBIFkeSa2ob.htm" 
        #doctor_url = "http://www.haodf.com/doctor/DE4r08xQdKSLPDMFJVGvdhaHfIMj.htm"
#        request = Request(doctor_url,callback=self.parse_doctor)
#        request.meta['city'] = u'上海'
#        yield request
#        return
        
        hospital_url = 'http://www.haodf.com/hospital/DE4roiYGYZwXhYmS30yF9V0wc.htm'
        request = Request(hospital_url, callback=self.parse_hospital)
        request.meta['city'] = u'上海'
        yield request
        return
    
#        hospital_url = 'http://www.haodf.com/hospital/DE4rO-XCoLUmJUoOljbt3pIpm0.htm'#        request = Request(hospital_url, callback=self.parse_hospital)
#        request.meta['city'] = u'西藏'
#        yield request
#        return
    
#        faculty_url = 'http://www.haodf.com/faculty/DE4rO-XCoLU0Jq1rbc1P6dS2aO.htm'
#        request = Request(faculty_url, callback=self.parse_doctors)
#        request.meta['city'] = u'上海'
#        yield request
#        return
            
        hxs = Selector(response)
        # Request for different city
        for city_url in hxs.xpath("//div[@id='el_tree_1000000']/div[@class='kstl']/a/@href").extract():
            yield Request(city_url, callback=self.parse) 
        
        city = hxs.xpath('//div[@class="kstl2"]/a/text()')[0].extract()
        
        hospital_relative_urls = hxs.xpath("//div[@class='m_ctt_green']/ul/li/a/@href").extract()
        for hospital_relative_url in hospital_relative_urls:
            base_url = get_base_url(response)
            hospital_absolute_url = urlparse.urljoin(base_url, hospital_relative_url)
#            print '..........................', hospital_absolute_url
            request = Request(hospital_absolute_url, callback=self.parse_hospital)
            request.meta['city'] = city
            yield request
        
    def parse_hospital(self, response):
        hxs = Selector(response)
        department_urls = hxs.xpath("//table[@id='hosbra']//tr/td/a[@class='blue']/@href").extract()
        for department_url in department_urls:
            request = Request(department_url, callback=self.parse_doctors)
            request.meta['city'] = response.meta['city']
            yield request
            
    #doctors next page
    def parse_doctors(self, response):
        hxs = Selector(response)
        #next page process
        next_page_url_list = hxs.xpath(u"//a[text()='下一页']/@href").extract() #/@href
        if len(next_page_url_list) != 0:
            next_page_url = next_page_url_list[0]
            base_url = get_base_url(response)
            print 'next_page_url is ',  next_page_url
            print 'base_url is ', base_url
            absolute_url = urlparse.urljoin(base_url, next_page_url)
            request = Request(absolute_url, callback=self.parse_doctors)
            request.meta['city'] = response.meta['city']
            yield request
        
        doctor_urls = hxs.xpath("//td[@class='tda']/li/a[not(img)]/@href").extract()
        for doctor_url in doctor_urls:
            request = Request(doctor_url, callback=self.parse_doctor)
            request.meta['city'] = response.meta['city']
            yield request



    def parse_doctor(self, response):
        response_url = response.url
        doctor_id = re.search('doctor/([^\.]*)\.htm', response_url).group(1) 

        hxs = Selector(response)
        f.write(hxs.extract())
        
        #parse doctor name
        name_list = hxs.xpath("//input[@name='doctor_name']/@value")
        doctor_name = ''
        if len(name_list) != 0:
            doctor_name = name_list[0].extract()
        
        #hospital department
        hospital = ''
        department = ''
        hd_selectors = hxs.xpath("//div[@class='luj']")
        if len(hd_selectors) != 0:
            hospital_selectors = hd_selectors.xpath("a[contains(@href, '/hospital/')]/text()")
            if len(hospital_selectors) == 1:
                hospital = hospital_selectors[0].extract()
            department_selectors = hd_selectors.xpath("a[contains(@href, '/faculty/')]/text()")
            if len(department_selectors) == 1:
                department = department_selectors[0].extract()

#        hospital_department_selectors = hxs.xpath("//meta[@name='keywords']/@content")
#        hospital_department_selectors2 = hxs.xpath("//html")
#        print "------------------hospital length: %s" % len(hospital_department_selectors2)
#        if len(hospital_department_selectors) != 0:
#            hospital_re = r',(?P<hospital>.*?)' + doctor_name
#            hospital_match = re.search(hospital_re, hospital_department_selectors[0].extract())
#            if hospital_match != None:
#                hospital = hospital_match.group('hospital')
#            
#            department_re = hospital + r'(?P<department>.*?)' + doctor_name + ','
#            department_match = re.search(department_re, hospital_department_selectors[0].extract())
#            if department_match != None:
#                department = department_match.group('department')
        
        #disease
        disease_poll_count_re = re.compile(u"(?P<poll_count>\d+)票")
        disease_polls = []
        disease_selectors = hxs.xpath('//div[@class="ltdiv"]//a')
        for ds in disease_selectors:
            ds_name_selectors = ds.xpath('text()')
            if len(ds_name_selectors) != 0:
                ds_dict = dict()
                ds_dict['name'] = ds_name_selectors[0].extract()
                poll_selectors = ds.xpath('following-sibling::text()')
                if len(poll_selectors) != 0:
                    poll_count_match = disease_poll_count_re.search(poll_selectors[0].extract())
                    if poll_count_match:
                        ds_dict['count'] = poll_count_match.group('poll_count')
                disease_polls.append(ds_dict)


        #title
        title = ''
        title_selectors = hxs.xpath(u"//td[text()='职　　称：']/following-sibling::td/text()")
        if len(title_selectors) == 1:
            title_re = re.compile(u"(?P<title>\S+医师)")
            title_match = title_re.search(title_selectors[0].extract())
            if title_match:
                title = title_match.group("title")

#        if title == '':
#            title_selectors = hxs.xpath('//meta[@name="description"]/@content')
#            if len(title_selectors) != 0:
#                title_re_str = doctor_name + r'(?P<doctor_title>.*?)' + u'简介'
#                title_found = re.search(title_re_str, title_selectors[0].extract())
#                if title_found:
#                    title = title_found.group(1)
        
        #parse in js: most condition
        #bp_doctor_about_js_lists = hxs.xpath('//script[@type="text/javascript"]/text()').re(r'BigPipe.onPageletArrive\(\{"id":"bp_doctor_about".*')

        #personal_image
        image_url = ''
#        if len(bp_doctor_about_js_lists) != 0:
#            image_re = re.compile(r'center.*?src=\\"(?P<img_js_url>.*?)\\"')
#            image_match = image_re.search(bp_doctor_about_js_lists[0])
#            if image_match != None:
#                image_url = image_match.group(1).replace('\/', '/')
                
        #parse in div
        if image_url == '':
            image_selectors = hxs.xpath("//div[@class='ys_tx']/table//tr/td/img/@src")
            if len(image_selectors) != 0:
                image_url = image_selectors[0].extract()
        
        feature = ''
        bio = ''
        #bio div full
        #//td/div[@id="full"] 
        if bio == "":
            bio_selectors = hxs.xpath('//div[@id="full"]')
            if len(bio_selectors) != 0:
                special_img_selectors = bio_selectors.xpath('.//img')
                if len(special_img_selectors) == 0: # no special img
                    content = bio_selectors[0].extract()
                    bio_re = re.compile(r'id="full"[^>]*>[/s]*(.*?)<span>', re.S)
                    bio_match = bio_re.search(content)
                    if bio_match != None:
                        bio = bio_match.group(1)
                        bio = bio.replace('<br>', '\n')
                        comment_re = re.compile('<!--.*?-->')
                        bio = comment_re.sub('', bio)
                        
#        if len(bp_doctor_about_js_lists) != 0:
#            content = bp_doctor_about_js_lists[0]
#            nr_re = re.compile(r'\\n|\\r|\\t|\xa0')
#            content = nr_re.sub('', content)
#
#            #bio js full
#            if bio == "":
#                if len(bp_doctor_about_js_lists) != 0:
#                    js_special_img_re = re.compile('giftrans')
#                    js_special_img_match = js_special_img_re.search(bp_doctor_about_js_lists[0])
#                    if js_special_img_match == None: # no replacement image
#                        bio_re = re.compile(r'<div id=\\"full\\"[^>]*>(?P<bio>.*?)<span>', re.S)
#                        bio_match = bio_re.search(content)
#                        if bio_match != None:
#                            bio = bio_match.group(1)#.decode('unicode_escape')
#
#            #bio js truncate: not contain giftrans
#            if bio == "":
#                bio_re = re.compile(r'div[ ]id=\\"truncate\\"[^>]*>[\s]*(?P<bio>.*?)[\s]*<span>', re.S)
#                bio_match = bio_re.search(content)
#                if bio_match != None:
#                    bio = bio_match.group(1)
#            #bio js not full or truncate 
#            if bio == "":
#                bio_re = re.compile(r'\\u6267\\u4e1a\\u7ecf\\u5386\\uff1a.*?<td[^>]*>(?P<bio_content>.*?)<br', re.S) # <!--.?--> only in full bio
#                bio_match = bio_re.search(content)
#                if bio_match != None:
#                    bio = bio_match.group(1)
#            
#            #bio filter
#            if bio != "":        
#                bio = bio.replace('<br \/>', '\n')
#                comment_re = re.compile('<!--.*?-->')
#                bio = comment_re.sub('', bio)
#                bio = bio.decode('unicode_escape')
#                print bio
#                             
#            #feature, bio js truncate
#            if feature == "":
#                feature_re = re.compile(r'truncate_DoctorSpecialize[^>]*>[\s]*(?P<feature>[\S]*)\s')
#                feature_match = feature_re.search(content)
#                if feature_match != None:
#                    feature =  feature_match.group(1).decode('unicode_escape')
                   
        #feature bio fetch through div
        if feature == "":
            feature_selectors = hxs.xpath('//div[@id="truncate_DoctorSpecialize"]/text()')
            if len(feature_selectors) != 0:
                feature = feature_selectors[0].extract()
                
        #bio div truncate        
        if bio == "":
            bio_selectors = hxs.xpath('//div[@id="truncate"]/text()')
            if len(bio_selectors) != 0:
                bio = bio_selectors[0].extract()
        
        #bio not in truncate div, in td
        #no div[@id='truncate'] or div[@id='full'] exists in such condition
#        if bio == "":
#            bio_xpath = '//td[text()="' + u'执业经历：' + '"]/parent::*/td[3]/text()'
#            bio_selectors = hxs.xpath(bio_xpath)
#            if len(bio_selectors) != 0:
#                for bio_sel in bio_selectors:
#                    bio += bio_sel.extract()
        if bio == "":
            bio_xpath = '//td[text()="' + u'执业经历：' + '"]/parent::*/td[3]'
            bio_selectors = hxs.xpath(bio_xpath)
            if len(bio_selectors) != 0:
                bio_re = re.compile("<td.*?>(?P<bio_content>.*?)<br", re.S)
                bio_match = bio_re.search(bio_selectors[0].extract())
                if bio_match != None:
                    bio = bio_match.group(1)

        zhanwu_re = re.compile(u'暂无')
        if zhanwu_re.search(bio) != None:
            bio = ''
        if zhanwu_re.search(feature) != None:
            feature = ''
         
        #format filter
        format_filter_re = re.compile(r'(<a .*?>|<\\/a>|\n|\t|\r|\\| )')
        if bio != "":
            bio = format_filter_re.sub('', bio)
        if feature != "":
            feature = format_filter_re.sub('', feature)
            
        #schedule
        doctor_schedule = []
        trs = hxs.xpath("//table[@class='doctortimefrom1']//tr")
        day_part = 0
        for itr in trs:
            if 0 != day_part:
                doctor_schedule.extend(self.weekday_operation(itr, day_part)) #上午
            day_part += 1
            
        item = DoctorDetailItem()
        item['doctor_id'] = doctor_id
        item['_name'] = doctor_name
        item['city'] = response.meta['city']
        item['hospital'] = hospital
        item['department'] = department
        item['title'] = title
        item['schedule'] = doctor_schedule
        item['feature'] = feature
        item['bio'] = bio
        if image_url:
            item['image'] = image_url
        if disease_polls:
            item['disease'] = disease_polls
        yield item 
           
    def weekday_operation(self, itr, day_part):
        tds = itr.xpath('td')
        tdl = []
        day = 0
        for itd in tds:
            r = self.fetch_properties(itd, day, day_part)
            if r != None:
                tdl.append(r)
            day += 1
        return tdl
                        
    def fetch_properties(self, td_selector, day, day_part):
        operation_type = td_selector.xpath('span/@title')
        if len(operation_type) != 0:
            ret = {}
            ret['operation_type'] = operation_type.extract()[0]
            content_list_origin = td_selector.xpath('text()').re('^\S.*')
            ret['content'] = []
            for iter in content_list_origin:
                ret['content'].append(iter.strip())
            ret['day'] = self.weekday_dict[day]
            ret['day_part'] = self.day_part_dict[day_part]
            return ret
        return None
