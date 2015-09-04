from scrapy.item import Item, Field

class LetterItem(Item):
    comment = Field()
    doctor_id = Field()
