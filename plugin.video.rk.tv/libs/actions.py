# -*- coding: utf-8 -*-
# Module: actions
# Author: Roman V.M.
# Created on: 09.06.2015
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""Plugin actions"""

import os
import re
import urllib
import xbmc
import xbmcplugin
from xbmcgui import Dialog
from simpleplugin import Plugin
from torrent_info import get_torrents
import tvdb
from gui import FilterList
from autodownloader import load_filters, save_filters
import datetime
now = datetime.datetime.now()


__all__ = ['plugin']

title_regex = re.compile(r'^(.+?)\.(?:s\d+e\d+|\d+x\d+)\.', re.I)
forbidden_chars_regex = re.compile(r'[<>:"/\\|\?\*]', re.I)
plugin = Plugin()
icons = os.path.join(plugin.path, 'resources', 'icons')
tv_icon = os.path.join(icons, 'tv.png')
commands = os.path.join(plugin.path, 'libs', 'commands.py')
dialog = Dialog()

def _set_info(list_item, torrent, myshows=False):
    """
    Set show and episode info for a list_item

    :param list_item: SimplePlugin list item to be updated
    :type list_item: dict
    :param torrent: torrent data
    :type torrent: dict
    :param myshows: ``True`` if the item is displayed in "My Shows"
    :type myshows: bool
    """
    video = {}
    torrent['show_info'] = None
    #torrent['tvdb_episode_info'] = None
    if torrent.get('episode_info'):
#        video['season'] = int(torrent['episode_info']['seasonnum'])
        video['season'] = 3
#        video['episode'] = int(torrent['episode_info']['epnum'])
        video['episode'] = 5
        if video.has_key('plot'):
            pass
        else:
            video['plot'] = video['plotoutline'] = 'This torrent is downloaded from '+plugin.get_setting('tr-name')+' on '+torrent['pubdate']

    if torrent.get('show_info') is not None:
        video['genre'] = torrent['show_info'].get('Genre', '').lstrip('|').rstrip('|').replace('|', ', ')
        video['cast'] = torrent['show_info'].get('Actors', '').lstrip('|').rstrip('|').split('|')
        video['mpaa'] = torrent['show_info'].get('ContentRating', '')
        video['tvshowtitle'] = list_item['label2'] = torrent['show_info'].get('SeriesName', '')
        video['plot'] = video['plotoutline'] = torrent['show_info'].get('Overview', '')
        video['studio'] = torrent['show_info'].get('Network', '')
        if torrent['show_info'].get('FirstAired'):
            video['year'] = int(torrent['show_info']['FirstAired'][:4])
    if torrent.get('tvdb_episode_info') is not None:
        video['director'] = torrent['tvdb_episode_info'].get('Director', '',)
        video['credits'] = torrent['tvdb_episode_info'].get('Writer', '').lstrip('|').rstrip('|').replace('|', ', ')
        video['premiered'] = (torrent['tvdb_episode_info'].get('FirstAired', '') or
                              torrent['episode_info'].get('airdate', ''))
        if torrent['tvdb_episode_info'].get('Rating'):
            video['rating'] = float(torrent['tvdb_episode_info']['Rating'])
        if myshows:
            video['plot'] = video['plotoutline'] = torrent['tvdb_episode_info'].get('Overview', '')
            list_item['label'] = (torrent['tvdb_episode_info'].get('EpisodeName') or
                                  torrent['episode_info'].get('title') or
                                  torrent['title'])
    video['title'] = list_item['label']
    list_item['info'] = {'video': video}


def _set_art(list_item, torrent, myshows=False):
    """
    Set graphics for a list_item

    :param list_item: SimplePlugin list item to be updated
    :type list_item: dict
    :param torrent: torrent data
    :type torrent: dict
    :param myshows: ``True`` if the item is displayed in "My Shows"
    :type myshows: bool
    """
    if torrent['show_info'] is not None:
        if torrent.get('tvdb_episode_info') is not None and myshows:
            list_item['thumb'] = list_item['icon'] = (torrent['tvdb_episode_info'].get('filename', '') or
                                                      torrent['show_info'].get('poster', ''))
        else:
            list_item['thumb'] = list_item['icon'] = torrent['show_info'].get('poster', '')
        list_item['fanart'] = torrent['show_info'].get('fanart', plugin.fanart)
        list_item['art'] = {'poster': torrent['show_info'].get('poster', ''),
                            'banner': torrent['show_info'].get('banner', '')}
    else:
        list_item['thumb'] = list_item['icon'] = tv_icon
        list_item['fanart'] = plugin.fanart


def _set_stream_info(list_item, torrent):
    """
    Set additional video stream info.

    :param list_item: SimplePlugin list item to be updated
    :type list_item: dict
    :param torrent: torrent data
    :type torrent: dict
    """
    video = {}
    resolution_match = re.search(r'(720|1080)[pi]', torrent['title'], re.I)
    if resolution_match is not None and resolution_match.group(1) == '720':
        video['width'] = 1280
        video['height'] = 720
    elif resolution_match is not None and resolution_match.group(1) == '1080':
        video['width'] = 1920
        video['height'] = 1080
    else:
        video['width'] = 720
        video['height'] = 480
    codec_match = re.search(r'[hx]\.?264|xvid|divx|mpeg2', torrent['title'], re.I)
    if codec_match is not None:
        if codec_match.group(0).endswith('264'):
            video['codec'] = 'h264'
        elif codec_match.group(0) == 'mpeg2':
            video['codec'] = 'mpeg2video'
        else:
            video['codec'] = codec_match.group(0)
    list_item['stream_info'] = {'video': video}


def _enter_search_query():
    """
    Enter a search query on Kodi on-screen keyboard.
    """
    keyboard = xbmc.Keyboard('', 'Enter search text')
    keyboard.doModal()
    text = keyboard.getText()
    if keyboard.isConfirmed() and text:
        query = urllib.quote_plus(text)
    else:
        query = ''
    return query


def _list_torrents(torrents, myshows=False):
    """
    Show the list of torrents

    :param torrents: list
    """
    for torrent in torrents:
        plugin.log_debug(str(torrent))
        if torrent['seeders'] <= 10:
            seeders = '[COLOR=red]{0}[/COLOR]'.format(torrent['seeders'])
        elif torrent['seeders'] <= 25:
            seeders = '[COLOR=yellow]{0}[/COLOR]'.format(torrent['seeders'])
        else:
            seeders = str(torrent['seeders'])
        list_item = {'label': '{title} [COLOR=gray]({size}MB|S:{seeders}/L:{leechers})[/COLOR]'.format(
                                title=torrent['title'],
                                size=int(torrent['size']) / 1048576,
                                seeders=seeders,
                                leechers=torrent['leechers']),
                     'url': plugin.get_url(action='play', torrent=torrent['download']),
                     'is_playable': True,
                     }
        _set_info(list_item, torrent, myshows)
        _set_art(list_item, torrent, myshows)
        _set_stream_info(list_item, torrent)
        list_item['info']['video']['mediatype'] = 'episode'
        if torrent['show_info'] is not None:
            show_title = re.sub(forbidden_chars_regex, '', torrent['show_info']['SeriesName'])
        else:
            title_match = re.search(title_regex, torrent['title'])
            if title_match is not None:
                show_title = title_match.group(1)
            else:
                show_title = torrent['title']
        list_item['context_menu'] = [('Show info', 'Action(Info)'),
                                     ('Mark as watched/unwatched', 'Action(ToggleWatched)'),
                                     ('Download torrent',
                                      u'RunScript({commands},download,{torrent},{show_title})'.format(
                                          commands=commands,
                                          torrent=torrent['download'],
                                          show_title=show_title)
                                      ),
                                     ('Add autodownload filter',
                                      u'RunScript({commands},add_filter,{tvdb},{show_title})'.format(
                                          commands=commands,
#                                          tvdb=torrent['episode_info']['tvdb'],
                                          tvdb=25,
                                          show_title=show_title)
                                      )]
        if myshows:
            list_item['context_menu'].append(
                ('Torrent info',
                 'RunScript({commands},torrent_info,{title},{size},{seeders},{leechers})'.format(
                    commands=commands,
                    title=torrent['title'],
                    size=torrent['size'] / 1048576,
                    seeders=torrent['seeders'],
                    leechers=torrent['leechers'])))
        else:
            list_item['context_menu'].append(('Add to "My shows"...',
                                              'RunScript({commands},myshows_add,{tvdb})'.format(
                                                  commands=commands,
                                                  tvdb=20)))
#                                                  tvdb=torrent['episode_info']['tvdb'])))
        yield list_item


@plugin.action()
def root():
    """
    Plugin root
    """
    listing = [
        {'label': 'My shows',
        'thumb': os.path.join(icons, 'bookmarks.png'),
        'icon': os.path.join(icons, 'bookmarks.png'),
        'fanart': plugin.fanart,
        'url': plugin.get_url(action='my_shows'),
       },
       {'label': 'TamilHD',
        'thumb': os.path.join(icons, 'hd.jpg'),
        'icon': tv_icon,
        'fanart': plugin.fanart,
        'url': plugin.get_url(action='hdepisodes', qlty='1080p', mode='list'),
        },
       {'label': 'TamilHD-720',
        'thumb': os.path.join(icons, 'hd.jpg'),
        'icon': tv_icon,
        'fanart': plugin.fanart,
        'url': plugin.get_url(action='hdepisodes', qlty='720p', mode='list'),
        },
       {'label': 'TamilRockers',
        'thumb': os.path.join(icons, 'tr.jpg'),
        'icon': tv_icon,
        'fanart': plugin.fanart,
        'url': plugin.get_url(action='hdepisodes', qlty='all', mode='list'),
        },
       {'label': '[Search torrents...]',
        'thumb': os.path.join(icons, 'search.png'),
        'icon': os.path.join(icons, 'search.png'),
        'fanart': plugin.fanart,
        'url': plugin.get_url(action='search_torrents')
       },
       {'label' : '[Autodownload Filters...]',
        'thumb' : os.path.join(icons, 'download.png'),
        'icon'  : os.path.join(icons, 'download.png'),
        'fanart': plugin.fanart,
        'url'   : plugin.get_url(action='autodownload'),
        'is_folder': False
        }
    ]
    return plugin.create_listing(listing, category='Rarbg TV Shows')


@plugin.action()
def hdepisodes(params):
    """
    Show the list of recent episodes
    """
    myshows = params.get('myshows', False)
    listing = _list_torrents(
        get_torrents(params['mode'],
                     params['qlty'],
                     search_imdb=params.get('search_imdb', ''),
                     episode_info='hd'),
        myshows=myshows)
    if myshows:
        content = 'episodes'
        sort_methods = (xbmcplugin.SORT_METHOD_EPISODE,)
    else:
        content = ''
        sort_methods = ()
    return plugin.create_listing(listing, content=content, sort_methods=sort_methods,
                                 category='Rarbg: Recent Episodes')
@plugin.action()
def episodes(params):
    """
    Show the list of recent episodes
    """
    myshows = params.get('myshows', False)
    listing = _list_torrents(
        get_torrents(params['mode'],
                     params['qlty'],
                     search_imdb=params.get('search_imdb', ''),
                     episode_info=myshows),
        myshows=myshows)
    if myshows:
        content = 'episodes'
        sort_methods = (xbmcplugin.SORT_METHOD_EPISODE,)
    else:
        content = ''
        sort_methods = ()
    return plugin.create_listing(listing, content=content, sort_methods=sort_methods,
                                 category='Rarbg: Recent Episodes')


@plugin.action()
def search_torrents():
    """
    Search torrents and show the list of results
    """
    results = []
    query = _enter_search_query()
    if query:
        results = get_torrents(mode='search', search_string=query)
        if not results:
            dialog.ok('Nothing found!', 'Adjust your search string and try again.')
    listing = _list_torrents(results)
    return plugin.create_listing(listing, cache_to_disk=True,
                                 category='Search Results for {0}'.format(query))


def _my_shows():
    with plugin.get_storage('myshows.pcl') as storage:
        myshows = storage.get('myshows', [])
    with plugin.get_storage('tvshows.pcl') as tvshows:
        for index, show in enumerate(myshows):
            if show not in tvshows:
                tvshows[show] = tvdb.get_series(show)
            list_item = {'label': tvshows[show]['SeriesName'],
                         'url': plugin.get_url(action='episodes',
                                               mode='search',
                                               search_imdb=tvshows[show]['IMDB_ID'],
                                               myshows='true'),
                         'context_menu': [('Show info', 'Action(Info)'),
                                          ('Remove from "My Shows"...',
                                           'RunScript({commands},myshows_remove,{index})'.format(
                                               commands=commands,
                                               index=index))]}
            _set_info(list_item, {'show_info': tvshows[show], 'tvdb_episode_info': None})
            _set_art(list_item, {'show_info': tvshows[show], 'tvdb_episode_info': None})
            list_item['info']['video']['mediatype'] = 'tvshow'
            yield list_item


@plugin.action()
def my_shows():
    """
    'My Shows' list
    """
    return plugin.create_listing(_my_shows(),
                                 content='tvshows',
                                 sort_methods=xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)


@plugin.action()
def play(params):
    """
    Play torrent via YATP
    """
    return plugin.get_url('plugin://plugin.video.yatp/', action='play', torrent=params['torrent'])


@plugin.action()
def autodownload():
    """
    Open the list of episode autodownload filters
    """
    filter_list = FilterList(load_filters())
    filter_list.doModal()
    if filter_list.dirty and dialog.yesno('Saving filters', 'Do you want to save filters?'):
        save_filters(filter_list.filters)
        dialog.notification('Rarbg', 'Autodownload filters saved.', icon=plugin.icon, time=3000, sound=False)
    del filter_list
