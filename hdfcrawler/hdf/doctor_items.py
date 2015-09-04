from scrapy.item import Item, Field

class DoctorDetailItem(Item):
    doctor_id = Field()
    _name = Field()
    city = Field()
    #area = Field()
    hospital = Field()
    department = Field()
    title = Field()
    image = Field()
    feature = Field()
    bio = Field()
    schedule = Field()
    disease = Field()
