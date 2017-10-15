# -*- coding: utf-8 -*-
# Module: parser
# Author: Roman V.M.
# Created on: 15.05.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
# Rarbg API docs: http://torrentapi.org/apidocs_v2.txt
import time
from simpleplugin import Plugin
from web_client import load_page
from rarbg_exceptions import RarbgApiError
import os, re
import bs4,time
import requests
import xbmcvfs
from bs4 import BeautifulSoup
import re,sqlite3
import urllib2
import xbmcgui

__all__ = ['load_torrents']

API = 'http://torrentapi.org/pubapi_v2.php'
plugin = Plugin('plugin.video.rk.tv')


def get_token():
    """
    Get a token to access Rarbg API

    The token will expire in 15 min

    :return: Rarbg API token
    :rtype: str
    """
    params = {'get_token': 'get_token'}
    return load_page(API, params=params, headers={'content-type': 'application/json'})['token']


@plugin.cached(15)
def load_torrents(params):
   mdata=[]
   plugin.log_warning ('Started fetching details for '+plugin.get_setting('tr-name'))
   url=plugin.get_setting('tr-name')
#   if params['qlty'] == 'hd':
#      url=plugin.get_setting('tr-name')
#   elif params['qlty'] == 'dub':
#      url=plugin.get_setting('tr-name')
#   elif params['qlty'] == 'dub':
#      url=plugin.get_setting('tr-name')
#   else:
#      url=plugin.get_setting('tr-name')
   try:
     response = requests.get(url,
                                  headers={'User-agent': 'Mozilla/5.0 (Windows NT '
                                                         '6.2; WOW64) AppleWebKit/'
                                                         '537.36 (KHTML, like '
                                                         'Gecko) Chrome/37.0.2062.'
                                                         '120 Safari/537.36'})
     soup = bs4.BeautifulSoup(response.content, "html.parser")
   except:
     response.status_code == 300
   if "blocked as per instructions" in response.content :
        xbmcgui.Dialog().notification('Rarbg', 'The URL has been blocked as per the instructions of Government Authority', 'error', 3000)
   if response.status_code == 200 and "blocked as per instructions" not in response.content  :
         for rk in soup.findAll(re.compile('.'),{'class':re.compile('.')}):
             if rk.get('href') == None or rk.text == '':
                 pass
             elif rk.text.startswith('['):
                  if '1080' in rk.text or '720' in rk.text:
  #                  plugin.log_warning ('   {}({})'.format(rk.text,rk['href']))
                     mdata.append(rk['href'])
             elif rk.text ==(':q!More'):
                 pass
             else:
  #              plugin.log_warning ('{}'.format(rk.text.split('[')[0]))
  #              plugin.log_warning ('   {}({})'.format(rk.text.split('[')[-1],rk['href']))
#                mdata.append(rk['href'])
                pass

   plugin.log_warning ('Fetching details..Completed--!')
   data={}
   rkr=[]
   folders, files = xbmcvfs.listdir(plugin.config_dir)
   path = os.path.join(plugin.config_dir, 'tr-torrent.db')
   conn = sqlite3.connect(path)
   cur = conn.cursor()
   for i in mdata:
      tid=int(re.findall('\d+',i)[0])
      cur.execute("select id from TROCKER where tid=?", (tid,))
      duptid = cur.fetchall()
      if duptid :
        pass
      else:
        r = requests.get(i)
        try:
           if r.status_code == 200:
                response = requests.get(r.url,
                                        headers={'User-agent': 'Mozilla/5.0 (Windows NT '
                                                               '6.2; WOW64) AppleWebKit/'
                                                               '537.36 (KHTML, like '
                                                               'Gecko) Chrome/37.0.2062.'
                                                               '120 Safari/537.36'})
                soup = bs4.BeautifulSoup(response.content, "html.parser")
                tamilmagnet=soup.find('a', href=re.compile('magnet'))['href']
                data['tid']=tid
                data['category']='TV HD Episodes'
                data['leechers']=20
                data['seeders']=30
                data['ranked']=1
                data['pubdate']=time.ctime()
                data['title']=soup.title.text
                data['download']=tamilmagnet
                data['info_page']=plugin.get_setting('tr-name')
                #data['show_info']=None
   #           data['episode_info']={'tvdb': '83051', 'tvrage': None, 'imdb': 'tt1128727', 'themoviedb': '12775'}
                data['episode_info']="{'title': 'Strife on Mars', 'tvdb': '281630', u'airdate': "+time.ctime()+", u'epnum': u'22', u'seasonnum': u'3', u'imdb': u'tt3514324', u'themoviedb': u'60797', u'tvrage': u'40717'}"
                data['size']=467749940
                row= [ data['tid'],data['category'],data['leechers'],data['seeders'],data['ranked'],data['pubdate'],data['title'],data['download'],data['info_page'],data['episode_info'],data['size'] ]
                query="INSERT INTO TROCKER VALUES (null,?,?,?,?,?,?,?,?,?,?,?)"
                conn.execute(query,row)
                conn.commit()
  #              rkr.append(data.copy())
        except Exception,e:
            plugin.log_warning (e) 

   plugin.log_warning ('This is complete') 
   def dict_factory(cursor, row):
       d = {}
       for idx, col in enumerate(cursor.description):
          d[col[0].lower()] = row[idx]
       return d
   print params['qlty']
   conn.row_factory = dict_factory
   cur = conn.cursor()
   if params.has_key('search_string'):
      cur.execute("select * from TROCKER where title like '%"+params['search_string' ]+"%'order by ID desc")
   elif params['qlty'] == '1080p':
      cur.execute("select * from TROCKER where title like '%"+params['qlty']+"%'order by ID desc")
   elif params['qlty'] == '720p':
      cur.execute("select * from TROCKER where title like '%"+params['qlty']+"%'order by ID desc")
   elif params['qlty'] == 'all':
      cur.execute("select * from TROCKER order by ID desc")
   else:
      cur.execute("select * from TROCKER order by ID desc")
   rkr = cur.fetchall()
   return rkr
