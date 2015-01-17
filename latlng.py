#! /usr/bin/python
# encoding=utf-8

import sys
import os
import urllib2
import json

__all__ = [
    'getLatLong',
    'getStdAddress',
    'getStdByAddress',
]

MAP_KEY='A0e7b6dc690da71f10bbaa3b3467e8ae'

def getLatLong(address):
    url = 'http://api.map.baidu.com/geocoder/v2/?ak=%s&output=json&address=%s' % (MAP_KEY, address)
    response = urllib2.urlopen(url, timeout = 10).read()
    json_loc = json.loads(response)
    if json_loc['status'] == 0:
        return json_loc['result']['location']
    else:
        return None


def getStdAddress(location):
    if not location:
        return None
    url = 'http://api.map.baidu.com/geocoder/v2/?ak=%s&output=json&location=%f,%f' % (MAP_KEY, location['lat'], location['lng'])
    response = urllib2.urlopen(url, timeout = 10).read()
    json_address = json.loads(response)
    if json_address['status'] != 0:
        return None
    return json_address['result']['addressComponent']


def getStdByAddress(address, times = 5):
    if times < 0:
        return None
    else:
        try:
            loc = getLatLong(address)
            stdaddress = getStdAddress(loc)
        except Exception,e:
            return getAddress(address, times-1)
        return stdaddress

