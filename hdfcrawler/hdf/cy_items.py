# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import MapCompose, Join, TakeFirst, Compose


class CYDoctorItem(Item):
    _name = Field(output_processor=TakeFirst(),)
    hospital = Field(output_processor=TakeFirst(),)
    specialty = Field(output_processor=TakeFirst(),)
    title = Field(output_processor=TakeFirst(),)
    specialtyDesc = Field(output_processor=TakeFirst(),)
    personalInfo = Field(output_processor=TakeFirst(),)
    stars = Field(output_processor=TakeFirst(),)
    answers = Field(output_processor=TakeFirst(),)
    reviews = Field(output_processor=TakeFirst(),)
