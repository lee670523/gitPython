# Scrapy settings for hdf project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'hdf'

SPIDER_MODULES = ['hdf.spiders']
NEWSPIDER_MODULE = 'hdf.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'hdf (+http://www.yourdomain.com)'

ITEM_PIPELINES = [
    'hdf.pipelines.DuplicatesPipeline',
    #'hdf.pipelines.JsonWriterPipeline',
    # 'hdf.pipelines.CSVWriterPipeline',
    'hdf.pipelines.MongoWriterPipeline',
]

USER_AGENT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

# LOG_ENABLED = True
# LOG_ENCODING = "utf-8"
# LOG_FILE = "hdf.log"
# LOG_LEVEL = "WARNING"
# LOG_STDOUT = True

#DOWNLOADER_MIDDLEWARES = {
#    'hdf.middlewares.WebkitDownloader': 543,
#}

#WEBKIT_DOWNLOADER=['schedule']

#import os
#os.environ["DISPLAY"] = ":0"
