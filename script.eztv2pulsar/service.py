# coding: utf-8
import re
import tools
import shelve
from xbmc import translatePath
from time import time
from time import asctime
from time import localtime
from time import strftime
from time import gmtime
from xbmc import log
from xbmc import sleep
from xbmc import abortRequested
from xbmcaddon import Addon


def update_service():
    path = translatePath('special://temp')
    database = shelve.open(path + 'EZTV2PULSAR.db')
    # this read the settings
    settings = tools.Settings(movie=False)
    # define the browser
    browser = tools.Browser()
    #Begin Service
    if settings.service == 'true':
        if database.has_key('list'):
            List_shows = database['list']
        else:
            List_shows = []
        if settings.time_noti > 0: settings.dialog.notification(settings.name_provider, 'Checking Online...', settings.icon, settings.time_noti)
        if len(List_shows) > 0:
            quality = settings.settings.getSetting('quality').lower()
            number = int(settings.settings.getSetting('number'))
            magnet_list = []
            file_list = []
            title_list = []
            for page in range(number + 1):
                if page == 0:
                    url_search = settings.url_address
                else:
                    url_search = '%s/page_%s' % (settings.url_address, str(page))
                if browser.open(url_search):
                    data = browser.content
                    for magnet in re.findall(r'magnet:\?[^\'"\s<>\[\]]+', data):
                        for show in List_shows:
                            name_file = magnet.lower()
                            if quality == 'hdtv' and ('720p' in name_file or '1080p' in name_file):
                                name_file = name_file.replace('hdtv', '')
                            if show.replace(' ', '.').lower() in name_file and quality in name_file:
                                magnet_list.append(magnet)
                                file_list.append(re.search('&dn=(.*?)&', magnet).group(1))
                                title_list.append(show)
                else:
                    settings.log('[%s]>>>>>>>%s<<<<<<<' % (settings.name_provider_clean, browser.status))
                    settings.dialog.notification(settings.name_provider, browser.status, settings.icon, 1000)
            tools.integration(filename=file_list, magnet=magnet_list, title=title_list, type_list='EPISODES', silence=True,
                            folder=settings.show_folder, name_provider=settings.name_provider)
        else:
            settings.dialog.notification(settings.name_provider, 'Empty List', settings.icon, settings.time_noti)
        database['list'] = List_shows
        database.sync()
        database.close()
    del settings
    del browser


if Addon().getSetting('service') == 'true':
    persistent = Addon().getSetting('persistent')
    name_provider = re.sub('.COLOR (.*?)]', '', Addon().getAddonInfo('name').replace('[/COLOR]', ''))
    every = 28800  # seconds
    previous_time = time()
    log("[%s] Update Service starting..." % name_provider)
    update_service()
    while (not abortRequested) and persistent == 'true':
        if time() >= previous_time + every:  # verification
            previous_time = time()
            update_service()
            log('[%s] Update List at %s' % (name_provider, asctime(localtime(previous_time))))
            log('[%s] Next Update in %s' % (name_provider, strftime("%H:%M:%S", gmtime(every))))
            update_service()
        sleep(500)
