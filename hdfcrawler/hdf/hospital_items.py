from scrapy.item import Item, Field
 
class HospitalItem(Item):
    hospital_id = Field()
    hospital_name = Field()
    city = Field()
    area = Field()
    grade = Field()
    feature = Field()
    address = Field()
    phone = Field()
