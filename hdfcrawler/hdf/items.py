# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import MapCompose, Join, TakeFirst, Compose


class CityItem(Item):
    # define the fields for your item here like:
    _cityName = Field(output_processor=TakeFirst(),)
    cityAreas = Field()


class HospitalItem(Item):
    _hospitalName = Field(output_processor=TakeFirst(),)
    grade = Field(output_processor=TakeFirst(),)
    feature = Field(input_processor=MapCompose(lambda v: v.strip()), output_processor=TakeFirst(),)
    city = Field(output_processor=TakeFirst(),)
    area = Field(output_processor=TakeFirst(),)


class DoctorItem(Item):
    _name = Field(output_processor=TakeFirst(),)
    hospital = Field(output_processor=TakeFirst(),)
    specialty = Field(output_processor=TakeFirst(),)
    title = Field(output_processor=TakeFirst(),)
    acadamicDegree = Field(output_processor=TakeFirst(),)
    shortDesc = Field(input_processor=MapCompose(lambda v: v.strip()), output_processor=TakeFirst(),)
    clinicTime = Field(output_processor=TakeFirst(),)


class ActiveDoctorItem(Item):
    _name = Field(output_processor=TakeFirst(),)
    hospital = Field(output_processor=TakeFirst(),)
    city = Field(output_processor=TakeFirst(),)
    area = Field(output_processor=TakeFirst(),)
    specialty = Field(output_processor=TakeFirst(),)
    title = Field(output_processor=TakeFirst(),)
    count_ReplyInTwoWeeks = Field(output_processor=TakeFirst(),)
    count_ReplyTotal = Field(output_processor=TakeFirst(),)
    count_Calls = Field(output_processor=TakeFirst(),)
    external_id = Field(output_processor=TakeFirst(),)
    comment = Field(output_processor=Join(),)

