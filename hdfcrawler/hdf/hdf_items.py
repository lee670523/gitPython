from scrapy.item import Item, Field

class DepartmentItem(Item):
    hospital_id = Field()
    hospital_name = Field()
    city = Field()
    area = Field()
    grade = Field()
    feature = Field()
    address = Field()
    phone = Field()
    department_category = Field()
    department_name = Field()

class HospitalItem(Item):
    hospital_id = Field()
    hospital_name = Field()
    city = Field()
    area = Field()
    grade = Field()
    feature = Field()
    address = Field()
    phone = Field()

class DiseaseItem(Item):
    disease_name = Field()
    disease_id = Field()
    category_0 = Field()
    category_1 = Field()
    category_2 = Field()
    hdf_doctor_recommend_number = Field()
    hdf_doctor_online_number = Field()
