#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import glob
import json
import os

from resources.lib.modules.utils import FileSearch
__addon__         = xbmcaddon.Addon('script.module.readme.changelog')
__addonsettings__ = __addon__.getSettings()
__setting__       = 'readme'

HOME = 10000

def GetList():
	addons = GetSysAddons()
	readmelist = []
	changeloglist = []
	for addon in addons:
		addonid = addon.get('addonid')
		addonpath = xbmcaddon.Addon(addonid).getAddonInfo('path')
		readmematches = FileSearch(addonpath,'readme.md',True)
		changelogmatches = FileSearch(addonpath,'changelog.*',True)
		if len(readmematches) >= 1:
			readmelist.append(addonid)
		if len(changelogmatches) >= 1:
			changeloglist.append(addonid)
	readmelist = ','.join(readmelist)
	changeloglist = ','.join(changeloglist)
	xbmcgui.Window(HOME).setProperty('READMELIST',readmelist)
	xbmcgui.Window(HOME).setProperty('CHANGELOGLIST',changeloglist)

	
def GetSysAddons():
	addons = xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","method":"Addons.GetAddons","params":{"enabled":True},"id":"1"}))
	addons = json.loads(addons)['result']['addons']
	return addons


if __name__ == '__main__':
	GetList()
