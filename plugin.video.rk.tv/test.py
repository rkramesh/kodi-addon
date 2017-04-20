#!/usr/bin/python
import os, re
import bs4,time
import requests
from bs4 import BeautifulSoup
import re
import urllib2
mdata=[]
tdata=[]
def load_torrents(url):
   print 'Started fetching details..'
#   mdata= [u'http://tamilrockers.im/index.php/topic/53443-risen-20161080p-bdrip-original-audio-dd51-384kbps-tamil-eng-x264-25gb-esubs/', u'http://tamilrockers.im/index.php/topic/53389-', u'http://tamilrockers.im/index.php/topic/53303-', u'http://tamilrockers.im/index.php/topic/53385-', u'http://tamilrockers.im/index.php/topic/53267-', u'http://tamilrockers.im/index.php/topic/53258-', u'http://tamilrockers.im/index.php/topic/53269-', u'http://tamilrockers.im/index.php/topic/53263-', u'http://tamilrockers.im/index.php/topic/53102-', u'http://tamilrockers.im/index.php/topic/53098-', u'http://tamilrockers.im/index.php/topic/53101-']
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
  
   if response.status_code == 200:
#     for tag in (soup.find_all('div',{'class':re.compile('ipsPad')})):
         for rk in soup.findAll(re.compile('.'),{'class':re.compile('.')}):
             if rk.get('href') == None or rk.text == '':
                 pass
             elif '/index.php/topic/' in rk['href']:
                   mdata.append(rk['href'])
             elif rk.text ==('More'):
                 pass
             else:
  #              print ('{}'.format(rk.text.split('[')[0]))
  #              print ('   {}({})'.format(rk.text.split('[')[-1],rk['href']))
#                mdata.append(rk['href'])
                pass
   
   print 'Fetching details..Completed!'
   mdata=set(mdata)
   data={}
   rk=[]
   for i in mdata:
      r = requests.get(i)
      print '\n'+r.url+'\n' 
      if r.status_code == 200: 
           response = requests.get(r.url,
                                   headers={'User-agent': 'Mozilla/5.0 (Windows NT '
                                                          '6.2; WOW64) AppleWebKit/'
                                                          '537.36 (KHTML, like '
                                                          'Gecko) Chrome/37.0.2062.'
                                                          '120 Safari/537.36'})
           soup = bs4.BeautifulSoup(response.content, "html.parser")

           tamilmagnet=soup.find('a', href=re.compile('magnet'))['href'] 
         #  print soup.find('p', src=re.compile('/images/'))['href'] 
           data['category']='TV HD Episodes'
           data['leechers']=20
           data['seeders']=30
           data['ranked']=1
           data['pubdate']='2017-04-16 14:40:19 +0000' 
           data['title']=soup.title.text
#           print soup.title.text
	   data['download']=tamilmagnet
           data['info_page']='http://test.rk.com'
           data['episode_info']={'tvdb': '83051', 'tvrage': None, 'imdb': 'tt1128727', 'themoviedb': '12775'}
           data['size']=467749940
           rk.append(data.copy()) 
   print rk
load_torrents('http://tamilrockers.im/index.php/forum/116-tamil-bluray-hd-movies')
