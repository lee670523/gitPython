# # -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.selector import HtmlXPathSelector, Selector
from scrapy.http import Request, HtmlResponse
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.link import Link

from hdf.items import CityItem, HospitalItem, DoctorItem
from hdf.doctor_items import DoctorDetailItem

import chardet
import codecs
from datetime import datetime
import json
import re
import urlparse

current_time = datetime.now().strftime('%Y%m%d%H%M%S')

def write_log(content):
    f = codecs.open(('/var/log/scrapy/schedule%s.log' % current_time), encoding='utf-8', mode='a+')
    f.write("%s\n" % content)

class OnsiteDoctorSpider(BaseSpider):
    name = "schedule"
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
#        doctor_url = "http://www.haodf.com/doctor/DE4r08xQdKSLBfkFK49LoalFRy9w.htm"
#        doctor_url = "http://www.haodf.com/doctor/DE4r08xQdKSLBfLu-dBIFkeSa2ob.htm"
#        doctor_url = "http://www.haodf.com/doctor/DE4r0BCkuHzduTWxaNkTMFHdvkQ4C.htm"
#        doctor_url = "http://www.haodf.com/doctor/DE4r08xQdKSLBfLu-dBIFkeSa2ob.htm"
#        doctor_url = "http://www.haodf.com/doctor/DE4r08xQdKSLBT0GOozM21bXlzuR.htm"
#        doctor_url = "http://www.haodf.com/doctor/DE4r0BCkuHzdeiqmLf0QBvLvytk8z.htm"
#        doctor_url = "http://www.haodf.com/doctor/DE4r0BCkuHzduTI-sthbpNCqpa7rv.htm"
#        request = Request(doctor_url,callback=self.parse_doctor)
#        request.meta['city'] = u'上海'
#        yield request
#        return
        
#        hospital_url = 'http://www.haodf.com/hospital/DE4roiYGYZwXhYmS30yF9V0wc.htm'
#        request = Request(hospital_url, callback=self.parse_hospital)
#        request.meta['city'] = u'上海'
#        yield request
#        return
    
#        hospital_url = 'http://www.haodf.com/hospital/DE4rO-XCoLUmJUoOljbt3pIpm0.htm'
#        request = Request(hospital_url, callback=self.parse_hospital)
#        request.meta['city'] = u'西藏'
#        yield request
#        return
    
#        hospital_url = 'http://www.haodf.com/hospital/DE4rO-XCoLU0jbqrbc1P6dS2aO.htm'
#        request = Request(hospital_url, callback=self.parse_hospital)
#        request.meta['city'] = u'新疆'
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
            request = Request(hospital_absolute_url, callback=self.parse_hospital)
            request.meta['city'] = city
            yield request
        
    def parse_hospital(self, response):
        hxs = Selector(response)
        department_urls = hxs.xpath("//table[@id='hosbra']/tr/td/a[@class='blue']/@href").extract()
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
            #print 'next_page_url is ',  next_page_url
            #print 'base_url is ', base_url
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
        
        #parse doctor name
        name_list = hxs.xpath("//input[@name='doctor_name']/@value")
        doctor_name = ''
        if len(name_list) != 0:
            doctor_name = name_list[0].extract()
        
        #hospital department
        hospital_department_selectors = hxs.xpath("//meta[@name='keywords']/@content") 
        hospital = ''
        department = ''
        if len(hospital_department_selectors) != 0:
            hospital_re = r',(?P<hospital>.*?)' + doctor_name
            hospital_match = re.search(hospital_re, hospital_department_selectors[0].extract())
            if hospital_match != None:
                hospital = hospital_match.group('hospital')
            
            department_re = hospital + r'(?P<department>.*?)' + doctor_name + ','
            department_match = re.search(department_re, hospital_department_selectors[0].extract())
            if department_match != None:
                department = department_match.group('department')
                
        #title
        title = ''
        title_selectors = hxs.xpath('//meta[@name="description"]/@content')
        if len(title_selectors) != 0:
            title_re_str = doctor_name + r'(?P<doctor_title>.*?)' + u'简介'
            title = re.search(title_re_str, title_selectors[0].extract()).group(1)
        
        doctor_about_dict = None
        tag_doctor_about_selectors = hxs.xpath('//div[@id="bp_doctor_about"]/div[@class="doctor_about"]')
        if len(tag_doctor_about_selectors) != 0:
            doctor_about_dict = self.parse_doctor_about(tag_doctor_about_selectors)
        else:
            doctor_about_match_list = hxs.xpath(
                '//script[@type="text/javascript"]/text()').re(
                'BigPipe.onPageletArrive\((?P<doctor_about>\{"id":"bp_doctor_about".*\})\);')
            if doctor_about_match_list:
                da_dict = json.loads(doctor_about_match_list[0])
                if 'content' in da_dict:
                    doctor_about_hxs = Selector(HtmlResponse(url=response.url, body=da_dict['content'].encode('utf-8')))
                    doctor_about_dict = self.parse_doctor_about(doctor_about_hxs)
            
            
        #schedule
        doctor_schedule = []
        trs = hxs.xpath("//table[@class='doctortimefrom1']/tr")
        day_part = 0
        for itr in trs:
            if 0 != day_part:
                doctor_schedule.extend(self.weekday_operation(itr, day_part)) #上午
            day_part += 1

        #disease
        disease_list = list()
        disease_ht_selector = hxs.xpath('//div[@class="ltdiv"]//table[@class="jbsm"]//td')
        if len(disease_ht_selector) == 1:
            disease_list = self.parse_disease_from_td_selector(disease_ht_selector, doctor_id=doctor_id)
        else:
            disease_match_list = hxs.xpath(
                '//script[@type="text/javascript"]/text()').re(
                'BigPipe.onPageletArrive\((?P<dict_content>\{"id":"bp_doctor_getvote".*\})\);')

            if disease_match_list:
                disease_match = disease_match_list[0]
                d_dict = json.loads(disease_match)

                if 'content' in d_dict:
                    disease_hxs = Selector(HtmlResponse(url=response.url, body=d_dict['content'].encode('utf-8')))
                    disease_selector = disease_hxs.xpath('//div[@class="ltdiv"]//table[@class="jbsm"]//td')
                    if len(disease_selector) == 1:
                        disease_list = self.parse_disease_from_td_selector(disease_selector, doctor_id=doctor_id)

        
        zanwu_re = re.compile(u'暂无')
        empty_sub_re = re.compile(r'(<!--.*?-->|\n|\t|\r|[ ])')
            
        item = DoctorDetailItem()
        item['doctor_id'] = doctor_id
        if doctor_name:
            item['_name'] = doctor_name
        if response.meta['city']:
            item['city'] = response.meta['city']
        if hospital:
            item['hospital'] = hospital
        if department:
            item['department'] = department
        if title:
            item['title'] = title
        if doctor_schedule:
            item['schedule'] = doctor_schedule
        else:
            if len(hxs.xpath('//table[@class="doctortimefrom1"]')) == 0:
                for content in hxs.xpath('//script[@type="text/javascript"]/text()').extract():
                    if content.find('doctortimefrom1') != -1:
                        item['schedule']= '' # shouldn't exist in js
                        break


        if doctor_about_dict:
            if 'image_url' in doctor_about_dict:
                item['image'] = doctor_about_dict['image_url']
            if 'bio' in doctor_about_dict:
                bio = doctor_about_dict['bio']
                if zanwu_re.search(bio) != None:
                    bio = ''
                if bio:
                    item['bio'] = empty_sub_re.sub('', bio)
            if 'feature' in doctor_about_dict:
                feature = doctor_about_dict['feature']
                if zanwu_re.search(feature) != None:
                    feature = ''
                if feature:
                    item['feature'] = empty_sub_re.sub('', feature)

        if disease_list:
            item['disease'] = disease_list
        yield item 


    def parse_doctor_about(self, doctor_about_selector):
        image_url = None
        image_selectors = doctor_about_selector.xpath(
            './/div[@class="ys_tx"]/table//tr/td/img/@src')
        if len(image_selectors) != 0:
            image_url = image_selectors[0].extract()

        bio = None
        bio_full_selectors = doctor_about_selector.xpath('.//div[@id="full"]')
        if len(bio_full_selectors) != 0:
            interfere_image_selectors = bio_full_selectors.xpath('.//img')
            if len(interfere_image_selectors) == 0:
                bio_full_text_selectors = bio_full_selectors.xpath('text()')
                bio = ''.join(bio_full_text_selectors.extract())

        if not bio:
            bio_truncate_text_selectors = doctor_about_selector.xpath(
                './/div[@id="truncate"]/text()')
            if len(bio_truncate_text_selectors) != 0:
                bio = ''.join(bio_truncate_text_selectors.extract())

        if not bio:
            bio_normal_selectors = doctor_about_selector.xpath(u'.//td[text()="执业经历："]/parent::tr/td[3]/text()')
            if len(bio_normal_selectors) != 0:
                bio = ''.join(bio_normal_selectors.extract())

        feature = None
        feature_selectors = doctor_about_selector.xpath('.//div[@id="truncate_DoctorSpecialize"]/text()')
        if len(feature_selectors) != 0:
            feature = ''.join(feature_selectors.extract())
        ret_dict = dict()
        if image_url:
            ret_dict['image_url'] = image_url
        if bio:
            ret_dict['bio'] = bio
        if feature:
            ret_dict['feature'] = feature
        return ret_dict


    def parse_disease_from_td_selector(self, td_selector, doctor_id=None):
        poll_count_re = re.compile(u'\((\d+)票\)')
        text_re = re.compile('\S+')
        disease_list = list()
        # a/text()
        disease_selector1 = td_selector.xpath('a')
        if len(disease_selector1) > 0:
            for ds in disease_selector1:
                ds_name_selectors = ds.xpath("text()")
                if len(ds_name_selectors) == 1:
                    disease_dict = dict()
                    disease_dict['name'] = ds_name_selectors[0].extract()
                    poll_count_selector = ds.xpath("following-sibling::text()[1]")
                    if len(poll_count_selector) != 0:
                        poll_count_match = poll_count_re.search(poll_count_selector[0].extract())
                        if poll_count_match:
                            disease_dict['count'] = poll_count_match.group(1)
                    disease_list.append(disease_dict)
        # text()
        disease_selector2 = td_selector.xpath('text()')
        for ds in disease_selector2:
            text_match = text_re.findall(ds.extract())
            tm_len = len(text_match)
            if tm_len > 1:
                i = 0
                while i < tm_len:
                    text_count_match = poll_count_re.search(text_match[i])
                    if not text_count_match:
                        disease_dict = dict()
                        disease_dict['name'] = text_match[i]
                        try:
                            text_count_match = poll_count_re.search(text_match[i+1])
                            if text_count_match:
                                disease_dict['count'] = text_count_match.group(1)
                        except:
                            write_log("doctor_id: %s, disease name: %s" % (doctor_id, disease_dict['name']))
                            pass
                        disease_list.append(disease_dict)
                    i += 1
        return disease_list
           
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
            content = []
            for iter in content_list_origin:
                content.append(iter.strip())
            if content:
                ret['content'] = content
            ret['day'] = self.weekday_dict[day]
            ret['day_part'] = self.day_part_dict[day_part]
            return ret
        return None
