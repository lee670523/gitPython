from scrapy.item import Item, Field

class DoctorDiseaseItem(Item):
    doctor_id = Field()
    disease_list = Field()
