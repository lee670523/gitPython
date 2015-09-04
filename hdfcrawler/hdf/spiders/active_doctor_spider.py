# # -*- coding: utf-8 -*-

from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.loader import XPathItemLoader
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.link import Link
from scrapy.shell import inspect_response

from hdf.items import CityItem, HospitalItem, DoctorItem, ActiveDoctorItem

import urlparse
import json
import re


class ActiveDoctorSpider(BaseSpider):
    name = "active"
    allowed_domains = ["haodf.com"]
    start_urls = [
        "http://www.haodf.com/yiyuan/all/list.htm",
    ]
    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(SgmlLinkExtractor(allow=(r'http://www.haodf.com/yiyuan/\w+/list.htm', )), follow=True, callback='parse_item'),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        #Rule(SgmlLinkExtractor(allow=('item\.php', )), callback='parse_item'),
    )

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        city_tree = hxs.select("//div[@id='el_tree_1000000']")

        current_city = hxs.select("//div[@class='kstl2']/a/text()").extract()
        #print "current city: {%s}" % current_city[0]

        for url in city_tree.select("div[@class='kstl']/a/@href").extract():
            yield Request(url, callback=self.parse)

        area_list = hxs.select("//div[@id='el_result_content']/div/div[@class='bxmd']/div/div[@class='m_ctt_green']")
        for area in area_list:
            area = area.select("preceding-sibling::div")[-1].select("./@id").extract()
            #print "current area: {%s}" % area[0]

            hospital_list = area_list.select("ul/li/a[contains(@href, '/hospital/')]")
            #hospital_list = area_list.select("ul/li/a[@href = '/hospital/DE4roiYGYZwXKEo-DwIIFQwlR.htm']")

            for url in hospital_list.select("@href").extract():
                base_url = get_base_url(response)
                relative_url = url
                absoluteUrl = urlparse.urljoin(base_url, relative_url)
                print absoluteUrl
                retReq = Request(absoluteUrl, callback=self.parse_hospital_detail)
                retReq.meta['city'] = current_city
                retReq.meta["area"] = area
                yield retReq

    def parse_hospital_detail(self, response):
        """ This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url http://www.haodf.com/hospital/DE4roiYGYZwXhYmS30yF9V0wc.htm
        @returns items 0 0
        @returns requests 1 1
        """

        hxs = HtmlXPathSelector(response)

        # if response.url != "http://www.haodf.com/hospital/DE4roiYGYZwXhYmS30yF9V0wc.htm":
        #     city = CityItem()
        #     yield city

        daifuLinks = hxs.select(u"//td[contains(text(), '咨询大夫')]/a")

        for url in daifuLinks.select("@href").extract():
            print url
            request = Request(url, callback=self.parse_hospital_active_doctor)
            if 'city' in response.meta and 'area' in response.meta:
                request.meta['city'] = response.meta['city']
                request.meta["area"] = response.meta['area']
            print "### current city: %s area: %s" % (response.meta['city'][0], response.meta['area'][0])
            yield request

    def parse_hospital_active_doctor(self, response):
        """ This function parses a sample response. Some contracts are mingled
        with this docstring.

        @url http://www.haodf.com/hospital/DE4roiYGYZwXhYmS30yF9V0wc/DE4rO-XCoLU0Jq1rbc1P6dS2aO/daifu.htm
        @returns items 14 14
        @returns requests 20 100
        @scrapes _name hospital specialty title reply2wCount
        """
        hxs = HtmlXPathSelector(response)

        city = response.meta['city']
        area = response.meta['area']
        print "$$$ current city: %s area: %s" % (city[0], area[0])

        #Sample
        #http://www.haodf.com/hospital/DE4roiYGYZwXhYmS30yF9V0wc/DE4rO-XCoLUE-578VWVmvC3uh7/daifu.htm

        linkExtractor = SgmlLinkExtractor(allow=(r"/hospital/\S+/\S+/daifu.htm",), unique=True)
        links = linkExtractor.extract_links(response)
        for link in links:
            request = Request(link.url, callback=self.parse_hospital_active_doctor)
            request.meta['city'] = response.meta['city']
            request.meta["area"] = response.meta['area']
            yield request

        next_page_url_list = hxs.xpath(u"//a[text()='下一页']/@href").extract() #/@href
        if len(next_page_url_list) != 0:
            next_page_url = next_page_url_list[0]
            base_url = get_base_url(response)
            #print 'next_page_url is ',  next_page_url
            #print 'base_url is ', base_url
            absolute_url = urlparse.urljoin(base_url, next_page_url)
            request = Request(absolute_url, callback=self.parse_hospital_active_doctor)
            request.meta['city'] = response.meta['city']
            request.meta["area"] = response.meta['area']
            yield request

        hospital = hxs.select('//div[@id="headpA_blue"]/div[@id="ltb"]/span[1]/a[1]/text()').extract()[0]
        print hospital
        specialty = hxs.select("//div[@class='subnav']/a/text()").re(r'(\S+)\s+(\S+)')[0]
        print specialty

        docLinks = hxs.select("//table[@id='doc_list_index']/tr[descendant::td[contains(@class, 'tda')]]")
        #docLinks = hxs.select("//table[@id='doc_list_index']/tr")

        for doc in docLinks:
            l = XPathItemLoader(ActiveDoctorItem(), doc)

            docNames = doc.select("./td[@class='tda']/li/a[contains(@href, 'http://www.haodf.com/doctor/')]/text()").extract()

            if len(docNames) != 0:
                print docNames[0]

            l.add_xpath('_name', "./td[@class='tda']/li/a[contains(@href, 'http://www.haodf.com/doctor/')]/text()")
            l.add_value('specialty', specialty)
            l.add_value('hospital', hospital)
            l.add_value('city', response.meta['city'])
            l.add_value('area', response.meta['area'])

            link=doc.select("./td[@class='tda']/li/a[contains(@href, 'http://www.haodf.com/doctor/')]/@href").extract()
            url=link[0]
            external_id = re.split('[/.]',url)[-2]
            url=url[:-4]+u'/jingyan/1.htm'
            l.add_value('external_id', external_id)

            title = doc.select("./td[@class='tda']/li/text()").re('\S+')

            if len(title) == 1:
                l.add_value('title', title[0])

            l.add_xpath('count_ReplyInTwoWeeks', u"./td[@class='td_hf']/div[contains(text(), '近2周回复咨询')]/span/text()")
            l.add_xpath('count_ReplyTotal', u"./td[@class='td_hf']/div[contains(text(), '总共回复')]/span/text()")
            l.add_xpath('count_Calls', u"./td[@class='td_hf']/div[contains(text(), '已接听电话咨询')]/span/text()")
            # ret = l.load_item()
            #print ret

            req=Request(url,callback=self.parse_letter)
            req.meta['item']=l
            yield req
    # def parse_letter(self,response):
    #     hxs=HtmlXPathSelector(response)
    #     letter=hxs.xpath("//table[@class='doctorjy']")
    #     temp=response.meta['item']
    #     letters=[]
    #     comment=''
    #     for l in letter:
    #         # patient=l.xpath(u"descendant::td[contains(text(),'患者：')]/text()").extract()
    #         # time=l.xpath(u"descendant::td[contains(text(),'时间：')]/text()").extract()
    #         # disease=l.xpath(u"descendant::td/span[contains(text(),'疾病：')]/following-sibling::a/text()").extract()
    #         # efficacy=l.xpath(u"descendant::td[contains(text(),'疗效：')]/span/text()").extract()
    #         c=''.join(l.xpath(u"descendant::td[@class='spacejy']/text()").extract()).strip()
    #         comment = comment + c

    #         # letters.append([patient[0],time[0],disease[0],efficacy[0],comment[0]])
    #     temp.add_value('comment',comment)
    #     ret=temp.load_item()
    #     yield ret


    def parse_letter(self,response):
        hxs=HtmlXPathSelector(response)

        next_page_url = hxs.xpath(u"//a[text()='下一页']/@href").extract()

        if len(next_page_url) != 0:
            flag = True
            request = Request(next_page_url[0], callback = self.parse_letter)
            request.meta['item'] = response.meta['item']
            yield request
        else:
            flag = False

        l = response.meta['item']
        letter=''
        letter1=hxs.xpath("//script").re('(?<=doctorjy).*?doctorjy')
        letter = letter + self.parse_letter_detail1(letter1)['letter']
        letter2=hxs.xpath("//table[@class='doctorjy']")
        letter = letter + self.parse_letter_detail2(letter2)['letter']

        l.add_value('comment',letter)

        if flag == True:
            yield None
        else:
            yield l.load_item()


    def parse_letter_detail1(self, letter_selector_1):

        letter = ''

        for i in range(1,len(letter_selector_1)):
            letter1[i]=re.sub('\xa0','',letter1[i])
            letter1[i]=letter1[i].decode("unicode-escape")
            time=u'时间：'+re.search(u'(?<=\u65f6\u95f4\uff1a).*(?=<)',letter1[i]).group()
            comment=u' 评论：'+re.search(u'(?<=spacejy">\n)(.*\t\t\t\t)([\s\S]*)(?=\t\t\t\t)',letter1[i]).group(2)

            letter = letter + time + comment
        return {'letter':letter}

    def parse_letter_detail2(self, letter_selector_2):
        letter = ''
        for l in letter_selector_2:
            patient=l.xpath(u"descendant::td[contains(text(),'患者：')]/text()").extract()[0]
            time=l.xpath(u"descendant::td[contains(text(),'时间：')]/text()").extract()[0]
            try:
                disease=l.xpath(u"descendant::td/span[contains(text(),'疾病：')]/following-sibling::a/text()").extract()[0]
            except:
                disease = u''
            try:
                efficacy=l.xpath(u"descendant::td[contains(text(),'疗效：')]/span/text()").extract()[0]
            except:
                efficacy = u''
            comment=u' 评论：'+''.join(l.xpath(u"descendant::td[@class='spacejy']/text()").extract()).strip()
            letter = letter + time + patient + u' 疾病:' + disease + u' 疗效：' + efficacy + comment

        return {'letter':letter}
