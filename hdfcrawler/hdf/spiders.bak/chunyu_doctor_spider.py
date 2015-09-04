# # -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.link import Link

from hdf.cy_items import CYDoctorItem

import urlparse
import json
import re

class ChunyuDoctorSpider(BaseSpider):
    name = "cy"
    allowed_domains = ["chunyuyisheng.com"]
    start_urls = [
        "http://www.chunyuyisheng.com/clinics/1/doctors",
    ]
    # rules = (
    #     # Extract links matching 'category.php' (but not matching 'subsection.php')
    #     # and follow links from them (since no callback means follow=True by default).
    #     Rule(SgmlLinkExtractor(allow=(r'http://www.haodf.com/yiyuan/\w+/list.htm', )), follow=True, callback='parse_item'),

    #     # Extract links matching 'item.php' and parse them with the spider's method parse_item
    #     #Rule(SgmlLinkExtractor(allow=('item\.php', )), callback='parse_item'),
    # )

    def parse(self, response):
        """ This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url http://www.chunyuyisheng.com/clinics/1/doctors
        @returns items 0 0
        @returns requests 500 100000
        """

        hxs = HtmlXPathSelector(response)

        listlinkExtractor = SgmlLinkExtractor(allow=(r"/clinics/\d+/doctors(|\?page=\d+)",), unique=True)
        list_links = listlinkExtractor.extract_links(response)
        for link in list_links:
            yield Request(link.url, callback=self.parse)


        docdetail_linkExtractor = SgmlLinkExtractor(allow=(r"/doctor/clinic_web_\w+$",), unique=True)
        docdetail_links = docdetail_linkExtractor.extract_links(response)
        for link in docdetail_links:
            yield Request(link.url, callback=self.parse_doctor_detail)



    def parse_doctor_detail(self, response):
        """ This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url http://www.chunyuyisheng.com/doctor/clinic_web_31f4d70d2867b969
        @returns items 1 1
        @returns requests 0 0
        """

        hxs = HtmlXPathSelector(response)


        l = XPathItemLoader(CYDoctorItem(), hxs)


        l.add_xpath('_name', ("//div[@class='bdHd']/h1/text()"))

        shortdesc = hxs.select("//div[@id='mainColumn']//p[@class='bdFt']/text()").extract()
        if len(shortdesc) == 1:
                shortdescStr = shortdesc[0].strip()
                words = shortdescStr.split()
                if len(words) == 3:
                    l.add_value('title', words[0])
                    l.add_value('hospital', words[1])
                    l.add_value('specialty', words[2])
                else:
                    print ("title/hostpital/special error.")



        l.add_xpath('specialtyDesc', "//div[@id='docOtherInfo']/div[@class='infoCell'][1]//p[2]/text()")
        l.add_xpath('personalInfo', "//div[@id='docOtherInfo']/div[@class='infoCell'][2]//p[2]/text()")
        l.add_xpath('stars', "//p[@class='right starTxt']/text()")

        answer = hxs.select("//div[@id='resolvedData']/p[1]/a/text()").extract()
        if len(answer) == 1:
            answerStr = answer[0].strip().replace(u"\xa0", "")
            m = re.match(u"解答:(?P<answer_cnt>\d+)", answerStr)
            if m.groupdict()["answer_cnt"]is not None:
                l.add_value('answers', m.groupdict()["answer_cnt"])

        review = hxs.select("//div[@id='resolvedData']/p[2]/text()").extract()
        if len(review) == 1:
            reviewStr = review[0].strip().replace(u"\xa0", "")
            m = re.match(u"评价:(?P<review_cnt>\d+)", reviewStr)
            if m.groupdict()["review_cnt"]is not None:
                l.add_value('reviews', m.groupdict()["review_cnt"])

        # l.add_xpath('answers', "//div[@id='resolvedData']/p[1]/a/text()")
        # l.add_xpath('reviews', "//div[@id='resolvedData']/p[2]/text()")

        ret = l.load_item()
        print ret

        yield ret
