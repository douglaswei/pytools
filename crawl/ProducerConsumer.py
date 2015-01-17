#! /usr/bin/python
# encoding:utf-8

import os
import sys
import logging
import re
import urllib2
from datetime import datetime
import time
from multiprocessing import Pool, Process, Manager
import threading
from Queue import Queue
import signal
import logging

MAX_THD_NUM = 1000

class TProducer(threading.Thread):
    def __init__(self, queue, consumer_num = MAX_THD_NUM):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.queue = queue
        self.consumer_num = consumer_num

    def run(self, *args):
        logging.info('start producer')
        self.produce_all(*args)
        for i in range(self.consumer_num):
            self.queue.put(None)
        logging.info('end producer')

    def produce_all(self, *args):
        time.sleep(1)
        self.queue.put(1)
        logging.info('producer, not implemented, put one element in q')


class TConsumer(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.queue = queue

    def run(self, *args):
        logging.info('start consumer')
        global is_exit
        while True:
            ret = self.consume_one(*args)
            if ret == -1:
                break
        logging.info('end consumer')

    def consume_one(self, *args):
        time.sleep(1)
        logging.info('consumer, not implemented, get one element from q')
        oneObj = self.queue.get()
        if not oneObj:
            logging.info('consumer: get None obj, exit')
            return -1


def handler(signum, frame):
    global is_exit
    logging.info('caught kill signal, set is_exit')
    is_exit = True
    sys.exit(-1)


def init_kill_signal():
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


def main():
    init_kill_signal()
    logging.basicConfig(level=logging.INFO, filename='log')
    q = Queue()
    for i in range(5):
        t = TConsumer(q)
        t.start()
    p = TProducer(q)
    p.start()
    alive = True
    while alive:
        alive = False
        alive = alive or p.isAlive()
        logging.info('p alive:' + str(alive))
        time.sleep(1)


if __name__ == '__main__':
    main()
