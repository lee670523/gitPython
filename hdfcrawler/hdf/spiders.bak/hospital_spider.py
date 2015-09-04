# # -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from hdf.items import CityItem, HospitalItem, DoctorItem, ActiveDoctorItem
import re


class HospitalSpider(BaseSpider):
    name = "hospital"
    allowed_domains = ["haodf.com"]
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

    def parse(self, response):
        """ This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url http://www.haodf.com/yiyuan/shanghai/list.htm
        @returns items 21 21
        @returns requests 3 3
        @scrapes _hospitalName grade area city
        """
        hxs = HtmlXPathSelector(response)

        city_tree = hxs.select("//div[@id='el_tree_1000000']")

        # Used for hospital
        _cityName = city_tree.select("div[@class='kstl2']/a/text()").extract()[0]

        l = XPathItemLoader(CityItem(), city_tree)
        l.add_xpath('cityAreas', "div[@class='ksbd']/ul/li/a/text()")
        l.add_xpath('_cityName', "div[@class='kstl2']/a/text()")
        yield l.load_item()

        for url in city_tree.select("div[@class='kstl']/a/@href").extract():
            yield Request(url, callback=self.parse)

        area_list = hxs.select("//div[@id='el_result_content']/div/div[@class='bxmd']/div")
        hospital_list = area_list.select("div[@class='m_ctt_green']/ul/li/a")
        for hospital in hospital_list:
            l = XPathItemLoader(HospitalItem(), hospital)
            l.add_xpath('_hospitalName', "text()")
            featureList = hospital.select("following-sibling::span/text()").extract()
            if len(featureList) == 1:
                featureStr = featureList[0].strip()
                m = re.match(u"\((?P<grade>\S+)(|, 特色:(?P<feature>\S+))\)", featureStr)
                if m is not None:
                    if m.groupdict()["grade"]is not None:
                        l.add_value('grade', m.groupdict()["grade"])
                    if m.groupdict()["feature"]is not None:
                        l.add_value('feature', m.groupdict()["feature"])
            #l.add_xpath('feature', "following-sibling::span/text()")
            l.add_xpath('area', "parent::*/parent::*/parent::*/preceding-sibling::*[1]/attribute::id")
            l.add_value('city', _cityName)
            yield l.load_item()

        # for url in hospital_list.select("@href").extract():
        #     print url
        #     yield Request(url, callback=self.parse_hospital_detail)

    # def parse_hospital_detail(self, response):
    #     hxs = HtmlXPathSelector(response)

    #     if response.url != "http://www.haodf.com/hospital/DE4roiYGYZwXhYmS30yF9V0wc.htm":
    #         city = CityItem()
    #         yield city

    #     facultyLinks = hxs.select("//table[@id='hosbra']/tbody/tr/td/a")
    #     for url in facultyLinks.select("@href").extract():
    #         yield Request(url, callback=self.parse_faculty_detail)

    # def parse_faculty_detail(self, response):
    #     hxs = HtmlXPathSelector(response)

    #     docLinks = hxs.select("//table[@id='doc_list_index']/tbody/tr/td/li/a")
    #     for doc in docLinks:
    #             l = XPathItemLoader(DoctorItem(), doc)
    #             l.add_xpath('name', "text()")
    #             yield l.load_item()
