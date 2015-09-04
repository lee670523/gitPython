# # -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.link import Link

from hdf.items import CityItem, HospitalItem, DoctorItem

import urlparse
import json


class Doctor2Spider(BaseSpider):
    name = "doctor"
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
        hxs = HtmlXPathSelector(response)

        city_tree = hxs.select("//div[@id='el_tree_1000000']")

        for url in city_tree.select("div[@class='kstl']/a/@href").extract():
            yield Request(url, callback=self.parse)

        area_list = hxs.select("//div[@id='el_result_content']/div/div[@class='bxmd']/div")
        hospital_list = area_list.select("div[@class='m_ctt_green']/ul/li/a[contains(@href, '/hospital/')]")
        #hospital_list = area_list.select("div[@class='m_ctt_green']/ul/li/a[@href = '/hospital/DE4roiYGYZwXhYmS30yF9V0wc.htm']")

        for url in hospital_list.select("@href").extract():
            base_url = get_base_url(response)
            relative_url = url
            absoluteUrl = urlparse.urljoin(base_url, relative_url)
            print absoluteUrl
            yield Request(absoluteUrl, callback=self.parse_hospital_detail)

    def parse_hospital_detail(self, response):
        """ This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url http://www.haodf.com/hospital/DE4roiYGYZwXhYmS30yF9V0wc.htm
        @returns items 0 0
        @returns requests 49 49
        """

        hxs = HtmlXPathSelector(response)

        # if response.url != "http://www.haodf.com/hospital/DE4roiYGYZwXhYmS30yF9V0wc.htm":
        #     city = CityItem()
        #     yield city

        facultyLinks = hxs.select("//table[@id='hosbra']/tr/td/a")
        for url in facultyLinks.select("@href").extract():
            print url
            yield Request(url, callback=self.parse_faculty_detail)

    def parse_faculty_detail(self, response):
        """ This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url http://www.haodf.com/faculty/DE4rO-XCoLU0Jq1rbc1P6dS2aO.htm
        @returns items 21 21
        @returns requests 3 3
        @scrapes _name specialty title shortDesc
        """
        hxs = HtmlXPathSelector(response)

        linkExtractor = SgmlLinkExtractor(allow=(r"/faculty/\S+/menzhen.htm\?orderby",), unique=True)
        links = linkExtractor.extract_links(response)
        for link in links:
            yield Request(link.url, callback=self.parse_faculty_detail)

        specialty = hxs.select("/html/body/div[3]/div/div[2]/div/a[3]/text()").extract()
        hospital = hxs.select("/html/body/div[3]/div/div[2]/div/a[2]/text()").extract()

        docLinks = hxs.select("//table[@id='doc_list_index']/tr[descendant::td[contains(@class, 'tda')]]")
        #docLinks = hxs.select("//table[@id='doc_list_index']/tr")

        for doc in docLinks:
                l = XPathItemLoader(DoctorItem(), doc)

                docNames = doc.select("./td[@class='tda']/li/a[contains(@href, 'http://www.haodf.com/doctor/')]/text()").extract()

                if len(docNames) != 0:
                    print docNames[0]

                l.add_xpath('_name', "./td[@class='tda']/li/a[contains(@href, 'http://www.haodf.com/doctor/')]/text()")
                l.add_value('specialty', specialty)
                l.add_value('hospital', hospital)
                l.add_xpath('title', "./td[@class='tda']/li/p[1]/text()")
                l.add_xpath('acadamicDegree', "./td[@class='tda']/li/p[2]/text()")
                l.add_xpath('shortDesc', "./td[@class='tdb']/text()")
                #clinic time todo

                ret = l.load_item()
                #print ret

                yield ret
