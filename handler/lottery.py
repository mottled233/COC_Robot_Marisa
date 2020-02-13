# -*- coding:gbk -*-

import os
import logging
import re
import random
import json
import requests
from bs4 import BeautifulSoup as bs

class Lottery:
	def __init__(self, url='https://www.zgjm.net/chouqian/guanyinlingqian/'):
		self.url = url
	
	def get_response(self, url):
		return requests.request('get', url)

	def draw(self):
		number = random.randint(1, 100)
		url = self.url + str(number) + '.html'
		res = self.get_response(url)
		result = self.parse_response(res)
		return result

	def parse_response(self, response):
		if not response.status_code == 200:
				return '无法连接到抽签网址'
		
		response.encoding = 'utf-8'
		soup = bs(response.text, 'html.parser')

		result = ''
		p_list = soup.find('article').children
		for p in p_list:
			text = ''
			try:
					text = p.text + "\n"
			except:
					pass
			result += text

		result += '\n每天只限一签哦'

		return result
