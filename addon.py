#!/usr/bin/python3
# -*- coding: utf-8 -*-
import xbmcaddon
import xbmcgui
import xbmcvfs

import os
import sys

from resources.lib.modules.utils import Log

__addon__     = xbmcaddon.Addon('script.module.readme.changelog')
__addonpath__ = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))

Log(str(sys.argv))
try:
	mode = sys.argv[1]
except:
	ret = xbmcgui.Dialog().select(__addon__.getLocalizedString(30007),[__addon__.getLocalizedString(30000),__addon__.getLocalizedString(30001)])
	Log(ret)
	if ret == 0:
		mode = 'readme'
	elif ret == 1:
		mode = 'changelog'

try:
	path = sys.argv[2]
except:
	path = None


if mode == 'readme':
	if not path:
		path = os.path.join(__addonpath__,'markdown-cheat-sheet.md')
	from userguide import UserGuide
	d=UserGuide('userguide.xml',__addonpath__,'Default','720p',mdfile=path)
	d.doModal()
	del d
		

elif mode == 'changelog':
	if not path:
		path = os.path.join(__addonpath__,'changelog.txt')
	from changelogview import ChangeLogView
	d=ChangeLogView('changelog.xml',__addonpath__,'Default',logpath=path)
	d.doModal()
	del d
	
		
