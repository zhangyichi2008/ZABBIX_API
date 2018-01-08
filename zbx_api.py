#!/usr/bin/python
# -*- coding: UTF-8 -*-
#By yichi1
#Mail: yichi1@staff.sina.com.cn

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import json
import urllib2
import re
import os
from operator import itemgetter

url = 'http://172.16.1.1/api_jsonrpc.php'
username = 'admin'
password = 'xxxxx'
hostname = sys.argv[1] + '.lb.sinanode.com'

class zbxapi:
	def __init__(self):
		self.url = url
		self.username = username
		self.password = password
		self.header = {"Content-Type": "application/json"}
		self.post_data = {
				 'jsonrpc': '2.0',
				 'method': '',
				 'params': '',
				 'auth': '',
				 'id': 0 }

	def _request(self):
		json_data = json.dumps(self.post_data)
		request = urllib2.Request(self.url,json_data,self.header)

                try:
                    response = urllib2.urlopen(request)  
                except URLError as e:
                    print "Error, Please Check:",e.code
                else:
                    out_data = json.loads(response.read())
                    response.close()
                    return out_data                    

	def _auth(self):
		self.post_data['method'] = 'user.login'
		self.post_data['params'] = {'user': self.username, 'password': self.password} 
		auth_out = self._request()
		self.post_data['auth'] = auth_out['result']
		self.post_data['id'] = 1

	def _getitem(self):
                self._auth()
		self.post_data['method'] = 'item.get'
		self.post_data['params'] = {"host":hostname,"output":["name","lastvalue"],"application":"LVS","search":{"name":"inbps"}} 
		getitem_out = self._request()
		getitem = getitem_out['result']
                return getitem

	def _getitemssl(self):
                self._auth()
		self.post_data['method'] = 'item.get'
		self.post_data['params'] = {"host":hostname,"output":["name","lastvalue"],"application":"SSL","search":{"name":"status"}} 
		getitemssl_out = self._request()
		getitemssl = getitemssl_out['result']
                return getitemssl

if sys.argv[2] == "lvs":
    zbx = zbxapi()
    zbx_vip = zbx._getitem()
    re_bps = re.compile(u'inbps') 
    dict_bps = {}
        
    for i in zbx_vip:
        if re_bps.search(i['name']):
            dict_bps[i['name']] = float(i['lastvalue'])/1000000
    a = sorted(dict_bps.iteritems(), key=itemgetter(1), reverse=True)
    for b in a:
        print b,'Mbps'

if sys.argv[2] == "ssl":
    zbx = zbxapi()
    zbx_ssl = zbx._getitemssl()
    re_qps = re.compile(u'请求次数') 
    re_inbps = re.compile(u'接收流量') 
    re_code50x = re.compile(u'状态码50X') 
    dict_qps = {}
    dict_inbps = {}
    dict_code50x = {}

    for i in zbx_ssl:
        if re_qps.search(i['name']):
            dict_qps[i['name']] = int(float(i['lastvalue']))
        elif re_inbps.search(i['name']):
            dict_inbps[i['name']] = float(i['lastvalue'])/1000000
        elif re_code50x.search(i['name']):
            dict_code50x[i['name']] = int(float(i['lastvalue']))
    a = sorted(dict_qps.iteritems(), key=itemgetter(1), reverse=True)
    b = sorted(dict_inbps.iteritems(), key=itemgetter(1), reverse=True)
    c = sorted(dict_code50x.iteritems(), key=itemgetter(1), reverse=True)
    print "----------------------------TOP 5 排名-----------------------------------"
    for m in a[0:10]:
        print m[0] +"  ======>" ,m[1],'qps'
    for n in b[0:10]:
        print n[0] +"  ======>" ,n[1],'Mbps'
    for l in c[0:10]:
        print l[0] +"  ======>" ,l[1],'次'
