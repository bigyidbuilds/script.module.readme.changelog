#!/usr/bin/python3
# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import sys


from resources.lib.modules.utils import FileSearch

__addon__ = xbmcaddon.Addon('script.module.readme.changelog')
__addonid__ = __addon__.getAddonInfo('id')

def showReadMe(addonid):
	addonpath = xbmcaddon.Addon(addonid).getAddonInfo('path')
	filelist = FileSearch(addonpath,'README.md',True)
	if len(filelist) >=1 and type(filelist) == list :
		file = filelist[0]
		xbmc.executebuiltin(f'RunScript({__addonid__},readme,{file})')

def showChangeLog(addonid):
	addonpath = xbmcaddon.Addon(addonid).getAddonInfo('path')
	filelist = FileSearch(addonpath,'changelog.*',True)
	if len(filelist) >=1 and type(filelist) == list :
		file = filelist[0]
		xbmc.executebuiltin(f'RunScript({__addonid__},changelog,{file})')
























if __name__ == '__main__':
	addonid   = xbmc.getInfoLabel('ListItem.Property(Addon.ID)')
	arg    = sys.argv[1]
	xbmc.log(str(sys.argv),level=xbmc.LOGINFO)
	xbmc.log(arg,level=xbmc.LOGINFO)
	if arg == 'readme':
		showReadMe(addonid)
	elif arg == 'changelog':
		showChangeLog(addonid)
