#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

__addon__        = xbmcaddon.Addon('script.module.readme.changelog')
__addonpath__    = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))



class ChangeLogView(xbmcgui.WindowXMLDialog):

	CLOSE = 1001
	TEXT  = 1006

	def __init__(self,*args,**kwargs):
		self.logpath = kwargs.get('logpath')
		self.logtext = self.ReadFile(self.logpath)

	def onInit(self):
		self.getControl(self.TEXT).setText(self.logtext)


	def onClick(self,controlId):
		xbmc.log(f'onClick:{str(controlId)}',level=xbmc.LOGINFO)
		if controlId == self.CLOSE:
			self.close()

	def ReadFile(self,logpath):
		with xbmcvfs.File(logpath) as f:
			return f.read()





# if __name__ == '__main__':
# 	d=ChangeLogView('changelog.xml',__addonpath__,'Default','720p',logpath=file)
# 	d.doModal()
# 	del d