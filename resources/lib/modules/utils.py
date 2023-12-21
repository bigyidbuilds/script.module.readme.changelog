#!/usr/bin/python3
# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon

import glob
import os

def FileSearch(path,filequery,recursive):
	return (glob.glob(os.path.join(path,'**',filequery),recursive=recursive))


def Log(msg):
	__addon__ = xbmcaddon.Addon('script.module.readme.changelog')
	if __addon__.getSettingBool('general.debug'):
		from inspect import getframeinfo, stack
		fileinfo = getframeinfo(stack()[1][0])
		xbmc.log('*__{}__{}*{} Python file name = {} Line Number = {}'.format(__addon__.getAddonInfo('name'),__addon__.getAddonInfo('version'),msg,fileinfo.filename,fileinfo.lineno), level=xbmc.LOGINFO)