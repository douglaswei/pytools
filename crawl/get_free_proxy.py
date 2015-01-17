#! /usr/bin/python
# encoding:utf-8

import os
import sys
import logging
import re
import urllib2
from datetime import datetime
import time
#from multiprocessing import Pool, Process, Manager
import threading
from Queue import Queue
import signal

from ProducerConsumer import TProducer, TConsumer, init_kill_signal, MAX_THD_NUM

http_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Cookie": "visid_incap_257263=hZZ3rUrvR/KT2aNAKs1ZjenToFQAAAAAQUIPAAAAAACG3nnf+LUrto9yxcfpc0X0; incap_ses_199_257263=N1o/ZjuMQW0XAs8DUx7DAunToFQAAAAABioeTfdjm85Vqxm+me0aXA==",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
}

#http_headers = {
#    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#    "Accept-Encoding":"gzip, deflate, sdch",
#    "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2",
#    "Connection":"keep-alive",
#    "Host":"www.xici.net.co",
#    "If-None-Match":"a24f838d651cb9ecda86d03e1826d6fe",
#    "RA-Sid":"7D628142-20140915-020456-83fd24-b1370b",
#    "RA-Ver":"2.8.6",
#    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
#}

# get http proxy from pages:
def getProxyFromUrl(url, proxy_re_patterns, sec=10, times=1):
    if times < 0:
        return []
    proxys = []
    req = urllib2.Request(url)
    for k,v in http_headers.items():
        req.add_header(k,v)
    try:
        response = urllib2.urlopen(req, timeout=sec).read()
    except Exception,e:
        return  getProxyFromUrl(url, proxy_re_patterns, sec, times-1)
    logging.debug('page content:' + response)
    for pattern in proxy_re_patterns:
        groups = re.findall(pattern, response)
        logging.debug(str(groups))
        for group in groups:
            proxys.append( 'http://%s:%s' % ('.'.join(group[:4]), group[4]))

    return proxys


# valide proxy, proxy format:   http://%s:%s@%s
def validateProxy(proxy, timeout=5):
    # use proxy to get baidu page
    beg_time = datetime.today()
    url = 'http://www.baidu.com'
    proxy_handler=urllib2.ProxyHandler({'http':proxy})
    opener=urllib2.build_opener(proxy_handler,urllib2.HTTPHandler)
    try:
        response=opener.open(url, timeout=timeout).read()
    except Exception,e:
        logging.debug('excetion caught' + str(e))
        return None
    if 'baidu' in response:
        end_time = datetime.today()
        diff = end_time - beg_time
        res =  diff.total_seconds()
        if res < timeout:
            return res
    return None


class proxyProducer(TProducer):
    def __init__(self, url_patterns, queue):
        TProducer.__init__(self, queue)
        self.url_patterns = url_patterns
        self.queue = queue


    def produce_all(self):
        for url,patterns in self.url_patterns.items():
            for proxy in getProxyFromUrl(url, patterns, 30, 3):
                logging.info('put proxy in q:\t' + proxy)
                self.queue.put(proxy)
        for i in range(MAX_THD_NUM):
            self.queue.put(None)


class proxyConsumer(TConsumer):
    def __init__(self, queue, lock):
        TConsumer.__init__(self, queue)
        self.queue = queue
        self.lock = lock

    def consume_one(self):
        proxy = self.queue.get()
        self.lock.acquire()
        self.lock.release()
        if proxy is None:
            return -1
        logging.info('q size:[%d] try to validate proxy:\t%s' % (self.queue.qsize(), proxy))
        span = validateProxy(proxy)
        if span:
            self.lock.acquire()
            print '\t'.join(['validate', proxy, str(span)])
            self.lock.release()


def main():
    logging.basicConfig(level=logging.INFO, filename='log')
    url_patterns = {
    }
    simple_patterns = [r'<td>(\d{1,3})\.(\d{1,3}).(\d{1,3}).(\d{1,3})</td>\s*<td>(\d+)</td>',]
    for idx in range(1, 30):
        url = 'http://www.proxy.com.ru/list_%d.html' % idx
        url_patterns[url] = simple_patterns
    for idx in range(5):
        if idx == 0:
            url = 'http://www.youdaili.net/Daili/http/2894.html'
        else:
            url = 'http://www.youdaili.net/Daili/http/2894_%d.html' % idx
        url_patterns[url] = [r'(\d{1,3})\.(\d{1,3}).(\d{1,3}).(\d{1,3}):(\d{1,3})@HTTP',]

    THD_NUM = 100
    consumers = []
    queue = Queue(MAX_THD_NUM * 2)
    mylock = threading.RLock()  

    for idx in range(THD_NUM):
        consumer = proxyConsumer(queue, mylock)
        consumers.append(consumer)
    
    producer = proxyProducer(url_patterns, queue)

    producer.start()
    for consumer in consumers:
        consumer.start()

    alive = True
    while alive:
        time.sleep(0.1)
        alive = False
        alive = alive or producer.isAlive()
        for consumer in consumers:
            alive = alive or consumer.isAlive()


if __name__ == '__main__':
    main()
