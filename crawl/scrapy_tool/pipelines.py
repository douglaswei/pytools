# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
from scrapy import log
from datetime import date

DUMP_FILENAME = './dump'


class DumpFilePipeline(object):
    def __init__(self):
        if not os.path.exists(DUMP_FILENAME):
            log.msg("file exists:[%s]" % DUMP_FILENAME)
        filename = DUMP_FILENAME + '_' + date.today().strftime('%Y%m%d')
        self.dump_file = open(filename, 'w')


    def process_item(self, item, spider):
        fields = [k+':'+v for k,v in item.items()]
        self.dump_file.write('\t'.join(fields).encode('utf-8') + '\n')
        return item


class DumpDBPipeline(object):
    def __init__(self):
        pass
