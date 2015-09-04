# # -*- coding: utf-8 -*-

import json
import csv
import codecs
import cStringIO
from scrapy.exceptions import DropItem
from hdf.hdf_items import DepartmentItem
from hdf.items import CityItem, DoctorItem, ActiveDoctorItem
from hdf.hospital_items import HospitalItem
from hdf.cy_items import CYDoctorItem
from datetime import datetime
import os
import pymongo
from hdf.doctor_items import DoctorDetailItem
from hdf.letter_items import LetterItem
from hdf.hdf_items import DiseaseItem
from hdf.doctor_disease_items import DoctorDiseaseItem
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

#DB Config
MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "hdf"
#MONGODB_COLLECTION_CITY = "city"
MONGODB_COLLECTION_DEPARTMENT = "department"
MONGODB_COLLECTION_HOSPITAL = "hospital"
MONGODB_COLLECTION_DOCTOR = "doctor"
MONGODB_COLLECTION_DOCTOR_SCHEDULE = "doctor_schedule"
MONGODB_COLLECTION_DOCTOR_DETAIL = "doctor"
MONGODB_COLLECTION_LETTER = "letter"
MONGODB_COLLECTION_ACTIVE = "active"
MONGODB_COLLECTION_DOCTOR_DISEASE = "doctor_disease"
#MONGODB_COLLECTION_DOCTOR_SCHEDULE = "ds2"

class ItemMeta(object):
    typeName = ""
    metaClass = HospitalItem
    keys = []
    enable = dict()

    def __init__(self, typeName, metaClass, keys, fields=None):
        self.typeName = typeName
        self.metaClass = metaClass
        self.keys = keys
        self.fields = metaClass.__dict__['fields'].keys()


itemMetaList = []
itemMetaList.append(ItemMeta("department", DepartmentItem, ['hospital_id', 'department_name'], ['hospital_id','hospital_name', 'city', 'area', 'grade', 'feature', 'address', 'phone', 'department_name', 'department_category']))
itemMetaList.append(ItemMeta("hospital", HospitalItem, ['hospital_id'], ['hospital_id','hospital_name', 'city', 'area', 'grade', 'feature', 'address', 'phone']))
itemMetaList.append(ItemMeta("city", CityItem, ["_cityName"], ["_cityName", "cityAreas"]))
itemMetaList.append(ItemMeta("doctor", DoctorItem, ["hospital", "specialty", "_name"]))
itemMetaList.append(ItemMeta("activedoctor", ActiveDoctorItem, ["hospital", "specialty", "_name"],))
itemMetaList.append(ItemMeta("cydoctor", CYDoctorItem, ["hospital", "specialty", "_name"],))
itemMetaList.append(ItemMeta("doctordetail", DoctorDetailItem, ["doctor_id", "_name", "city", "hospital", "title", "image", "feature", "bio", "schedule"]))
itemMetaList.append(ItemMeta("disease", DiseaseItem, ["disease_name", "category_0", "category_1"]))
itemMetaList.append(ItemMeta("letter", LetterItem, ["doctor_id"]))
itemMetaList.append(ItemMeta("doctor_disease", DoctorDiseaseItem, ["doctor_id"]))

class DuplicatesPipeline(object):
    def __init__(self):
        self.ids = dict()
        for meta in itemMetaList:
            self.ids[meta.typeName] = set()

    def process_item(self, item, spider):
        #not process DoctorDetailItem
        if isinstance(item, DoctorDetailItem):
            return item
        if isinstance(item, DiseaseItem):
            return item

        itemKey = ""

        for meta in itemMetaList:
            if isinstance(item, meta.metaClass):
                if len(meta.keys) == 1:
                    itemKey = item[meta.keys[0]]
                else:
                    itemKey = "-".join([item[k] for k in meta.keys])

                if itemKey in self.ids[meta.typeName]:
                    raise DropItem("Duplicate item found: %s" % item)
                else:
                    self.ids[meta.typeName].add(itemKey)
                    return item


class JsonWriterPipeline(object):
    def __init__(self):
        self.folderPath = "./data/" + datetime.now().strftime("%m%d_%H%M%S")
        self.jsonFiles = dict()

    def process_item(self, item, spider):

        if not os.path.exists(self.folderPath):
            os.makedirs(self.folderPath)

        line = json.dumps(dict(item), ensure_ascii=False, sort_keys=True) + "\n"

        for meta in itemMetaList:
            if isinstance(item, meta.metaClass):
                if meta.typeName not in self.jsonFiles or self.jsonFiles[meta.typeName] is None:
                    self.jsonFiles[meta.typeName] = codecs.open(self.folderPath + '/' + meta.typeName + '.json', 'w', encoding='utf-8')
                self.jsonFiles[meta.typeName].write(line)

        return item

    def spider_closed(self, spider):
        for meta in itemMetaList:
            if self.jsonFiles[meta.typeName] is not None:
                self.jsonFiles[meta.typeName].close()

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class CSVWriterPipeline(object):

    def __init__(self):
        self.folderPath = "./data/" + datetime.now().strftime("%m%d_%H%M%S")
        self.csvFiles = dict()
        self.csvWriters = dict()

    def process_item(self, item, spider):

        if not os.path.exists(self.folderPath):
            os.makedirs(self.folderPath)

        for meta in itemMetaList:
            if isinstance(item, meta.metaClass):
                if meta.typeName not in self.csvFiles or self.csvFiles[meta.typeName] is None:
                    #f = codecs.open(self.folderPath + '/' + meta.typeName + '.csv', 'w', encoding='utf-8')
                    f = open(self.folderPath + '/' + meta.typeName + '.csv', 'w')
                    f.write(u'\ufeff'.encode('utf-8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
                    w = csv.DictWriter(f, sorted(meta.fields))
                    w.writeheader()

                    self.csvFiles[meta.typeName] = f
                    self.csvWriters[meta.typeName] = w

                self.csvWriters[meta.typeName].writerow({k: v.encode('utf8') for k, v in item.items()})
                # csv_file.writerow(item.values())

        return item

    def spider_closed(self, spider):
        for meta in itemMetaList:
            if self.csvFiles[meta.typeName] is not None:
                self.csvFiles[meta.typeName].close()


class MongoWriterPipeline(object):
    def __init__(self):

        self.connection = pymongo.MongoClient(MONGODB_SERVER, MONGODB_PORT)
        self.db = self.connection[MONGODB_DB]
        self.collection_doctor = self.db[MONGODB_COLLECTION_DOCTOR]
        self.collection_doctor_schedule = self.db[MONGODB_COLLECTION_DOCTOR_SCHEDULE]
        self.collection_doctor_detail = self.db[MONGODB_COLLECTION_DOCTOR_DETAIL]
        self.collection_hospital = self.db[MONGODB_COLLECTION_HOSPITAL]
        self.collection_department = self.db[MONGODB_COLLECTION_DEPARTMENT]
        self.collection_letter = self.db[MONGODB_COLLECTION_LETTER]
        self.collection_active = self.db[MONGODB_COLLECTION_ACTIVE]
        self.collection_doctor_disease = self.db[MONGODB_COLLECTION_DOCTOR_DISEASE]

    def process_item(self, item, spider):
        if isinstance(item, HospitalItem):
            obj = dict(item)
            self.collection_hospital.insert(obj)
            return item
        elif isinstance(item, CityItem):
            return item
        elif isinstance(item, DoctorItem):
            obj = dict(item)
            #if not self.collection_doctor.find({"hospital": item["hospital"], "specialty":item["specialty"], "_name":item["_name"]}):
            self.collection_doctor.insert(obj)
            return item
        elif isinstance(item, DoctorDetailItem):
            obj = dict(item)
            self.collection_doctor_detail.insert(obj)
            return item
        elif isinstance(item, DepartmentItem):
            obj = dict(item)
            self.collection_department.insert(obj)
            return item
        elif isinstance(item, LetterItem):
            obj = dict(item)
            self.collection_letter.insert(obj)
            return item
        elif isinstance(item, ActiveDoctorItem):
            obj = dict(item)
            self.collection_active.insert(obj)
            return item
        elif isinstance(item, DoctorDiseaseItem):
            obj = dict(item)
            self.collection_doctor_disease.insert(obj)
            return item


