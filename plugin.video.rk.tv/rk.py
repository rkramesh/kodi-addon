#!/usr/bin/python
import os, re
import bs4,time
import requests
from bs4 import BeautifulSoup
import re
import urllib2
import sqlite3
data={}
rk=[]
conn = sqlite3.connect('tr-torrent.db')
mdata= [u'http://tamilrockers.im/index.php/topic/53443-risen-20161080p-bdrip-original-audio-dd51-384kbps-tamil-eng-x264-25gb-esubs/', u'http://tamilrockers.im/index.php/topic/53389-', u'http://tamilrockers.im/index.php/topic/53303-', u'http://tamilrockers.im/index.php/topic/53385-', u'http://tamilrockers.im/index.php/topic/53267-', u'http://tamilrockers.im/index.php/topic/53258-', u'http://tamilrockers.im/index.php/topic/53269-', u'http://tamilrockers.im/index.php/topic/53263-', u'http://tamilrockers.im/index.php/topic/53102-', u'http://tamilrockers.im/index.php/topic/53098-', u'http://tamilrockers.im/index.php/topic/53101-']
         #  print soup.find('p', src=re.compile('/images/'))['href'] 
data['id']=2
data['tid']='56342'
data['category']='TV HD Episodes'
data['leechers']=20
data['seeders']=30
data['ranked']=1
data['pubdate']='2017-04-16 14:40:19 +0000' 
data['title']='title.text'
#           print soup.title.text
data['download']='tamilmagnet'
data['info_page']='http://test.rk.com'
data['episode_info']="{'tvdb': '83051', 'tvrage': None, 'imdb': 'tt1128727', 'themoviedb': '12775'}"
data['size']=467749940
rk.append(data.copy()) 
# connector.execute("insert into TROCKER values (NULL,?,?,?,?,?,?,?,?,?,?)", *data)
conn.execute("insert into TROCKER values (NULL,:tid,:category,:leechers,:seeders,:ranked,:pubdate,:title,:download,:info_page,:episode_info)", data)
