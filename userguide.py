#!/usr/bin/python3
# -*- coding: utf-8 -*-
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from collections import namedtuple
from itertools import groupby,count
import math
import os
from PIL import Image
import re
import requests
import sys
from urllib.parse import quote,unquote
from urllib.request import urlopen
import webbrowser

from resources.lib.modules.utils import Log

__addon__        = xbmcaddon.Addon('script.module.readme.changelog')
__addonpath__    = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))
__addonprofile__ = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))


builtinMethod = 'RunScript(script.context.userguide,mdpath)'

syntaxs   = ['#','_','>','\n','|','[',']','(',')',':','-']
formatters = ['*','~','`']
newline = '\\n'



fonts = {'h1':{'name':'font60','height':50,'width':60},'h2':{'name':'font45','height':30,'width':45},'h3':{'name':'font37','height':27,'width':37},'h4':{'name':'font14','height':23,'width':14},'h5':{'name':'font13','height':20,'width':13},'h6':{'name':'font12','height':17,'width':8}}

ACTION_SELECT_ITEM = 7


class UserGuide(xbmcgui.WindowXMLDialog):

	'''Controls and Buttons'''
	CLOSE     = 1001
	PREVIOUS  = 1003
	NEXT      = 1004	
	PAGECOUNT = 1005

	def __init__(self,*args,**kwargs):
		self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
		self.headers = {"User-Agent":self.user_agent, "Connection":'keep-alive', 'Accept':'audio/webm,audio/ogg,udio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5'}
		self.itemumber = 1
		self.maxwidth = 1200
		self.maxheight = 635
		self.mdfile = kwargs.get('mdfile')
		self.pagecount = 0
		self.Pages = []
		self.onclick = []
		self.content = self.ParseMarkdown(self.FileLines())
		self.lastitem = len(self.content.keys())
		


	def onInit(self):
		DialogBusy().Open()
		self.DrawPages(self.itemumber)
		self.totalpages = len(self.Pages)
		self.Ncontrol = self.getControl(self.NEXT)
		self.Pcontrol = self.getControl(self.PREVIOUS)
		self.Xcontrol = self.getControl(self.CLOSE)
		self.LoadPage(self.pagecount)
		DialogBusy().Close()


	def onClick(self,controlId):
		xbmc.log(f'onClick:{str(controlId)}',level=xbmc.LOGINFO)
		visclick = []
		for i in self.onclick:
			cId = i[0].getId()
			if cId not in [self.NEXT,self.PREVIOUS,self.CLOSE]:
				visclick.append(cId)
		if controlId == self.PREVIOUS:
			if self.pagecount >=1:
				p = self.pagecount-1
				self.LoadPage(p,self.pagecount)
				self.pagecount = p
		elif controlId == self.NEXT:
			if self.pagecount < self.totalpages:
				p = self.pagecount+1
				self.LoadPage(p,self.pagecount)
				self.pagecount = p
		elif controlId in visclick:
			control = [x for x in self.onclick if x[0].getId() == controlId]
			if control:
				# xbmc.log(str(control),level=xbmc.LOGINFO)
				control = control[0]
				if control[1] == 'openurl':
					urls = control[2]
					if len(urls)>=2:
						d=UrlSelect('urlselect.xml',__addonpath__,'Default','720p',urls=urls)
						d.doModal()
						urltoview = d.selectedItem.getPath()
						del d
					else:
						urltoview = urls[0].get('link')
					WebViewer().View(urltoview)
				elif control[1] == 'enlargeimg':
					d=FullScreenImage(control[2])
					d.doModal()
					del d


	def setControlVisible(self, controlId, visible):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setVisible(visible)



	def LoadPage(self,page_no,prev_page=None):
		DialogBusy().Open()
		focusitems = []
		focusitems.append((self.Xcontrol,self.Xcontrol.getY()))
		nextvis = False
		prevvis = False
		onclick = []
		if prev_page != None:
			self.ClearPage(prev_page)
			xbmc.sleep(1000)
		self.getControl(self.PAGECOUNT).setLabel(f'Page {page_no+1}/{self.totalpages}')
		if page_no >= self.totalpages-1:
			self.setControlVisible(self.NEXT,False)
		else:
			self.setControlVisible(self.NEXT,True)
			nextvis = True
		if page_no == 0:
			self.setControlVisible(self.PREVIOUS,False)
		else:
			self.setControlVisible(self.PREVIOUS,True)
			prevvis = True
		if nextvis or (prevvis and nextvis):
			focusitems.append((self.Ncontrol,self.Ncontrol.getY()))
		elif not nextvis and prevvis:
			focusitems.append((self.Pcontrol,self.Pcontrol.getY()))
		page = self.Pages[int(page_no)]
		controls = [elem.control for elem in page]
		for control in controls:
			try:
				self.addControl(control)
			except:pass
			if control.__class__.__name__ == 'ControlButton':
				focusitems.append((control,control.getY()))
		orderedfocus = list(sorted(focusitems, key=lambda x: x[1]))
		if len(orderedfocus)>=2:
			for i,ctrl in enumerate(orderedfocus):
				if i == 0:
					ctrl[0].controlDown(orderedfocus[1][0])
				elif i == len(orderedfocus)-1:
					ctrl[0].controlUp(orderedfocus[i-1][0])
				else:
					ctrl[0].controlDown(orderedfocus[i+1][0])
					ctrl[0].controlUp(orderedfocus[i-1][0])
		for elem in page:
			if elem.control in [x[0] for x in focusitems]:
				onclick.append((elem.control,elem.item.get('func'),elem.item.get('hyperlink')))
		xbmc.sleep(1000)
		if nextvis and not prevvis:
			self.setFocusId(self.NEXT)
		elif prevvis and not nextvis:
			self.setFocusId(self.PREVIOUS)
		elif not prevvis and not nextvis:
			self.setFocusId(self.CLOSE)
		self.onclick = onclick
		DialogBusy().Close()
		


	def DrawPages(self,itemumber):
		self.itemumber = itemumber
		ControlandItemsList = []
		startpoint_x = 10
		startpoint_y = 20
		for k,v in list(self.content.items()):
			k = int(k)
			self.itemumber = k
			guitype = v.get('type')
			fontheight = fonts.get(v.get('headersize')).get('height')
			fontwidth = fonts.get(v.get('headersize')).get('width')
			if guitype == 'label':
				if startpoint_y+fontheight < self.maxheight:
					control = xbmcgui.ControlLabel(startpoint_x,startpoint_y,self.maxwidth,fontheight,v.get('label'),v.get('font'),'FF000000')
					ControlandItemsList.append(ControlAndItem(control,v))
					startpoint_y = startpoint_y+fontheight
					self.content.pop(str(k))
				else:
					break
			elif guitype == 'textbox':
				font = v.get('font')
				text = v.get('text',v.get('label'))
				blockheight = self.TextBlockSize(text,font)
				if startpoint_y+blockheight < self.maxheight:
					control = xbmcgui.ControlTextBox(startpoint_x, startpoint_y, self.maxwidth, blockheight, font, 'FF000000')
					control.setText(text)
					ControlandItemsList.append(ControlAndItem(control,v))
					startpoint_y = startpoint_y+blockheight
					self.content.pop(str(k))
				else:
					break
			elif guitype == 'button':
				font = v.get('font')
				text = v.get('text',v.get('label'))
				text = self.insertNewLine(text,font)
				blockheight = self.TextBlockSize(text,font)
				if startpoint_y+blockheight < self.maxheight:
					control = xbmcgui.ControlButton(startpoint_x, startpoint_y,self.maxwidth, blockheight, text,'invisible.png','invisible.png',font=v.get('font'), textColor='FF000000', focusedColor='FF00FFFF')
					ControlandItemsList.append(ControlAndItem(control,v))
					startpoint_y = startpoint_y+blockheight
					self.content.pop(str(k))
				else:
					break
			elif guitype == 'bquote':
				if startpoint_y+fontheight+10 < self.maxheight:
					control = xbmcgui.ControlImage(startpoint_x+10, startpoint_y-1, 5, fontheight+10,'rc-white-100.png', colorDiffuse='FF00FFFF')
					ControlandItemsList.append(ControlAndItem(control,v))
					control = xbmcgui.ControlLabel(startpoint_x+20,startpoint_y-1,self.maxwidth-20,fontheight+10,v.get('label'),v.get('font'),'FF000000',alignment=0x00000004)
					ControlandItemsList.append(ControlAndItem(control,v))
					startpoint_y = startpoint_y+fontheight+10
					self.content.pop(str(k))
				else:
					break
			elif guitype == 'nest_bquote':
				if startpoint_y+fontheight+10 < self.maxheight:
					control = xbmcgui.ControlImage(startpoint_x+10, startpoint_y-1, 5, fontheight+10,'rc-white-100.png', colorDiffuse='FF00FFFF')
					ControlandItemsList.append(ControlAndItem(control,v))
					control = xbmcgui.ControlImage(startpoint_x+20, startpoint_y-1, 5, fontheight+10,'rc-white-100.png', colorDiffuse='FF00FFFF')
					ControlandItemsList.append(ControlAndItem(control,v))
					control = xbmcgui.ControlLabel(startpoint_x+30,startpoint_y-1,self.maxwidth-30,fontheight+10,v.get('label'),v.get('font'),'FF000000',alignment=0x00000004)
					ControlandItemsList.append(ControlAndItem(control,v))
					startpoint_y = startpoint_y+fontheight+10
					self.content.pop(str(k))
				else:
					break
			elif guitype == 'table':
				a = []
				lines = v.get('text').split('\n')
				for l in lines:
					if l:
						a += l.split('|')[1:-1]
				longeststr = (len(max(a,key=len))+5)*fontwidth
				totalheight = len(lines)*fontheight
				if startpoint_y+totalheight < self.maxheight:
					lc = 0
					for line in lines:
						cc = 0
						posy = startpoint_y+(fontheight*lc)
						lc +=1 
						for x in line.split('|')[1:-1]:						
							posx = startpoint_x+(longeststr*cc)
							cc +=1
							control = xbmcgui.ControlLabel(posx,posy,longeststr,fontheight,x,v.get('font'),'FF000000')
							ControlandItemsList.append(ControlAndItem(control,v))
					startpoint_y = startpoint_y+totalheight
					self.content.pop(str(k))
				else:
					break
			elif guitype == 'image':
				imagepath = v.get('hyperlink')[0].get('link')
				# xbmc.log(imagepath,level=xbmc.LOGINFO)
				img = self.OpenImage(imagepath)
				img_w,img_h = self.ImageSize(img)
				maximgw = 200
				maximgh = 200
				if img_w < maximgw and img_h < maximgh:
					if startpoint_y+img_h+fontheight < self.maxheight:
						control = xbmcgui.ControlImage(startpoint_x,startpoint_y, img_w, img_h, imagepath,2)
						ControlandItemsList.append(ControlAndItem(control,v))
						startpoint_y = startpoint_y+img_h
						control = xbmcgui.ControlLabel(startpoint_x,startpoint_y,self.maxwidth,fontheight,v.get('label'),v.get('font'),'FF000000')
						ControlandItemsList.append(ControlAndItem(control,v))
						startpoint_y=startpoint_y+fontheight
						self.content.pop(str(k))
					else:
						break
				else:
					if img_w > maximgw:
						wpercent = (maximgw/float(img_w))
						img_h = int((float(img_h)*float(wpercent)))
						img_w = maximgw
					if img_h > maximgh:
						hpercent = (maximgh/float(img_h))
						img_w = int((float(img_w)*float(hpercent)))
						img_h = maximgh
					if startpoint_y+img_h+fontheight < self.maxheight:
						control = xbmcgui.ControlImage(startpoint_x,startpoint_y, img_w, img_h, imagepath,2)
						ControlandItemsList.append(ControlAndItem(control,v))
						startpoint_y = startpoint_y+img_h
						control = xbmcgui.ControlButton(startpoint_x, startpoint_y,self.maxwidth, fontheight,f"{v.get('label')}([I]Click to enlarge image[/I])",'invisible.png','invisible.png',font=v.get('font'), textColor='FF000000', focusedColor='FF00FFFF')
						ControlandItemsList.append(ControlAndItem(control,v))
						startpoint_y=startpoint_y+fontheight
						self.content.pop(str(k))
					else:
						break
		self.Pages.append(ControlandItemsList)
		try:
			if len(self.content.keys())>0:
				self.DrawPages(self.itemumber)
		except:
			return



	def insertNewLine(self,text,font):
		fontdetails = [v for v in fonts.values() if v.get('name')==font]
		if fontdetails:
			fontdetails = fontdetails[0]
		maxlinelen = math.floor(self.maxwidth/fontdetails.get('width'))
		if not '\n' in text and len(text) > maxlinelen:
			words = text.split(' ')
			linelen = 0
			for i,word in enumerate(words):
				linelen += len(word)+1
				if linelen > maxlinelen:
					toedit = words[i-1]
					words[i-1] = f'{toedit}\n'
					linelen = 0
			text = ' '.join(words)
		return text


	def TextBlockSize(self,text,font):
		fontdetails = [v for v in fonts.values() if v.get('name')==font]
		if fontdetails:
			fontdetails = fontdetails[0]
		if '\n' in text:
			ls = text.split('\n')
			rows = len(ls)
			for l in ls:
				form = (len(l)*fontdetails.get('width'))
				# xbmc.log(str(form),level=xbmc.LOGINFO)
				if form > self.maxwidth:
					rows += math.ceil(form/self.maxwidth)
			rows = math.ceil(rows*1.5)
			textheight = rows*fontdetails.get('height')
		else:
			form = (len(text)*fontdetails.get('width'))
			if form > self.maxwidth:
				rows = math.ceil((form/self.maxwidth))
				textheight = math.ceil(rows*(fontdetails.get('height')*1.5))
			else:
				textheight = fontdetails.get('height')*2
		return textheight


	def ClearPage(self,page):
		controls = [elem.control for elem in self.Pages[page]]
		try:
			self.removeControls(controls)
		except RuntimeError:
			for elem in self.Pages[page]:
				try:
					self.removeControl(elem.control)
				except RuntimeError:
					pass  # happens if we try to remove a control that doesn't exist


	def FileLines(self):
		if self.mdfile.startswith('http'):
			xbmc.log('mdfile is from url',level=xbmc.LOGINFO)
			return [x.decode('utf-8') for x in  urlopen(self.mdfile).readlines()]
		else:
			with open(self.mdfile,'r',encoding='utf-8') as f:
				xbmc.log('mdfile is from local',level=xbmc.LOGINFO)
				return f.readlines()

	def ImageSize(self,image):
		return image.size	

	def OpenImage(self,imagepath):
		if imagepath.startswith('http'):
			im = Image.open(requests.get(imagepath,headers=self.headers, stream=True).raw)
		else:
			im = Image.open(imagepath)
		return im


	def TextBoxModifiy(self,replacements,text):
		rep = dict((quote(k), v) for k, v in replacements.items()) 
		pattern = re.compile("|".join(rep.keys()))
		try:
			text = pattern.sub(lambda m: rep[m.group(0)], quote(text))
		except KeyError:
			text = text
		return unquote(text)


	def ParseMarkdown(self,filelines):
		catitems = {}
		counter = 0
		code = zip(*[iter([i for i, e in enumerate(filelines) if '```' in e])]*2)
		for start,stop in code:
			newitem = ''.join(filelines[start:stop+1])
			del filelines[start:stop+1]
			filelines.insert(start,newitem)
		table = groupby([i for i,e in enumerate(filelines) if e.startswith('|')], lambda n, c=count(): n-next(c))
		for _,t in table:
			x = list(t)
			start,stop = (x[0],x[-1])
			newitem = ''.join(filelines[start:stop+1])
			del filelines[start:stop+1]
			filelines.insert(start,newitem)
		for line in filelines:
			_type = None;label=None;font=None;hyperlink=None;text=None;function=None
			counter += 1
			line = line.strip()
			if any( s in syntaxs for s in line):
				if line.startswith('#'):
					header,label = re.compile(r'^(#.*?)\s(.+?$)').findall(line)[0]
					headersize = f'h{len(header)}'
					font = fonts.get(headersize).get('name')
					_type = 'label'
				elif line.startswith('>'):
					bquote,label = re.compile(r'^(.*?)\s(.+?$)').findall(line)[0]
					if len(bquote)==2:
						_type = 'nest_bquote'
					else:
						_type = 'bquote'
					headersize = 'h6'
					font = fonts.get(headersize).get('name')
					text = label
				elif line.startswith('|'):
					_type = 'table'
					headersize = 'h6'
					font = fonts.get(headersize).get('name')
					label = text = line
				elif line.startswith('```'):
					_type = 'textbox'
					label = line.strip('```\n')
					headersize = 'h6'
					font = fonts.get(headersize).get('name')
					text = label
				elif line.startswith('-'):
					_type = 'label'
					headersize = 'h6'
					label = line
					font = fonts.get(headersize).get('name')
				elif line.startswith(':'):
					_type = 'textbox'
					text = line.lstrip(':')
					headersize = 'h6'
					font = fonts.get(headersize).get('name')
				elif all(x in line for x in ['[',']','(',')']):
					replacements = {}
					rec = re.compile(r'\[(.*?)\]\((.*?)\)')
					matches = rec.findall(line)
					hyperlink = []
					for label,link in matches:
						hyperlink.append({'link':link,'label':label})
						replacements.update({f'[{label}]':"\u0332".join(f' {label} '),f'({link})':''})
					headersize = 'h6'
					if line.startswith('!['):
						_type = 'image'
						function = 'enlargeimg'
					else:
						_type = 'button'
						function = 'openurl'
						text = self.TextBoxModifiy(replacements,line)
					font = fonts.get(headersize).get('name')
			elif re.match(r"^\d+.*\.",str(line)):
				# ordered list
				_type = 'label'
				label = line
				text = label
				headersize = 'h6'
				font = fonts.get(headersize).get('name')
			elif len(line.strip())>0:
				_type = 'textbox'
				text = line
				headersize = 'h6'
				font = fonts.get(headersize).get('name')
			elif _type == None:
				# newline dection
				_type = 'label'
				headersize = 'h6'
				font = fonts.get(headersize).get('name')
			if label and any(s in formatters for s in label) or  text and any(s in formatters for s in text):
				if label and text:
					S = '|'.join([label,text])
				elif label and not text:
					S = label
				elif text and not label:
					S = text
				replacements = {}
				B=re.compile(r'(\*\*.*[a-z0-9]\*\*)').findall(S)
				I=re.compile(r'(\*.*[a-z0-9]\*)').findall(S)
				T=re.compile(r'(\~\~.+?\~\~)').findall(S)
				C=re.compile(r'(`.+?`)').findall(S)
				if B:
					for s in B:
						replacements.update({s:f"[B]{s.strip('**')}[/B]"})
				if I:
					for s in I:
						replacements.update({s:f"[I]{s.strip('*')}[/I]"})
				if T:
					for s in T:
						replacements.update({s:''.join([u'\u0336{}'.format(w) for w in s.strip('~~')])})
				if C:
					for s in C:
						replacements.update({s:f"[COLOR FF00FFFF]{s.strip('`')}[/COLOR]"})
				S = self.TextBoxModifiy(replacements,S)
				if '|' in S:
					label,text = S.split('|')
				else:
					label = text = S	
			catitems.update({str(counter):{'type':_type,'label':label,'font':font,'orig_string':line,'hyperlink':hyperlink,'text':text,'headersize':headersize,'func':function}})
		# xbmc.log(str(catitems),level=xbmc.LOGINFO)
		return catitems


class FullScreenImage(xbmcgui.WindowXMLDialog):

	IMG = 1001

	def __new__(cls,imagepath,*args,**kwargs):
		return super(FullScreenImage, cls).__new__(cls,'fullscreenimage.xml', __addonpath__, 'Default', '720p')


	def __init__(self,imagepath,*args,**kwargs):
		super(FullScreenImage,self).__init__()
		self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
		self.headers = {"User-Agent":self.user_agent, "Connection":'keep-alive', 'Accept':'audio/webm,audio/ogg,udio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5'}
		self.imagepath = imagepath[0].get('link')
		self.img_w,self.img_h = self.ImageSize(self.OpenImage(self.imagepath))

	def onInit(self):
		img_control = self.getControl(self.IMG)
		img_control.setImage(self.imagepath)
		if self.img_w < 1280 and self.img_h < 720:
			img_control.setWidth(self.img_w)
			img_control.setHeight(self.img_h)
			img_control.setPosition((1280-self.img_w)/2,(720-self.img_h))
		else:
			img_control.setPosition(0,0)
			img_control.setHeight(720)
			img_control.setWidth(1280)


	def ImageSize(self,image):
		return image.size	

	def OpenImage(self,imagepath):
		if imagepath.startswith('http'):
			im = Image.open(requests.get(imagepath,headers=self.headers, stream=True).raw)
		else:
			im = Image.open(imagepath)
		return im

class UrlSelect(xbmcgui.WindowXMLDialog):

	BACK  = 1000
	CLOSE = 1001
	LABEL = 1002
	LIST  = 1003
	GROUP = 2000

	selectedItem = None

	def __init__(self,*args,**kwargs):
		self.urls = kwargs.get('urls')
		self.listheight = len(self.urls)*50
		self.backheight = 60+self.listheight+5

	def onInit(self):
		self.getControl(self.GROUP).setPosition(415,int((720-self.backheight)/2))
		self.getControl(self.BACK).setHeight(self.backheight)
		self.getControl(self.LABEL).setLabel('Multiple hyperlink\'s found please select one' )
		self.listcontrol = self.getControl(self.LIST)
		self.listcontrol.setHeight(self.listheight)
		for u in self.urls:
			li = xbmcgui.ListItem(u.get('label'),path=u.get('link'))
			self.listcontrol.addItem(li)
		self.setFocusId(self.LIST)

	def onAction(self,action):
		if action == ACTION_SELECT_ITEM and self.getFocusId() == self.LIST:
			self.selectedItem = self.listcontrol.getSelectedItem()
			self.close()

	def onClick(self,controlId):
		if controlId == self.CLOSE:
			self.close()


class WebViewer():


	def __init__(self):
		self.platform = self.Platform()
		

	def View(self,url):
		if self.platform:
			if self.platform == 'Android':
				xbmc.executebuiltin(f'StartAndroidActivity(,android.intent.action.VIEW,,{url})')
			else:
				webbrowser.open(url)
		else:
			d=PopUpNotifiy('Unable to determine system platform',5000)
			d.doModal()
			del d



	def Platform(self):
		if xbmc.getCondVisibility('System.Platform.Linux') and not xbmc.getCondVisibility('System.Platform.Android'):
			return 'Linux'
		elif xbmc.getCondVisibility('system.platform.linux') and xbmc.getCondVisibility('system.platform.android'):
			return 'Android'
		elif xbmc.getCondVisibility('System.Platform.Windows'):
			return 'Windows'
		elif xbmc.getCondVisibility('System.Platform.UWP'):
			return 'UWP'
		elif xbmc.getCondVisibility('System.Platform.OSX'):
			return 'OSX' 
		elif xbmc.getCondVisibility('System.Platform.IOS'):
			return 'IOS'
		elif xbmc.getCondVisibility('System.Platform.TVOS'):
			return 'TVOS'
		elif xbmc.getCondVisibility('System.Platform.Darwin'):
			return 'Darwin'
		else:
			return None


class PopUpNotifiy(xbmcgui.WindowXMLDialog):

	TEXT = 1001

	def __new__(cls,text,time,*args,**kwargs):
		return super(PopUpNotifiy, cls).__new__(cls,'popupnotifiy.xml', __addonpath__, 'Default', '720p')


	def __init__(self,text,time,*args,**kwargs):
		self.text = text
		self.time = time


	def onInit(self):
		self.getControl(self.TEXT).setLabel(self.text)
		xbmc.sleep(self.time)
		self.close()



class ControlAndItem(object):
	def __init__(self, control, item):
		self.control = control
		self.item = item

class DialogBusy():

	Visible = False

	@staticmethod
	def Open():
		if not DialogBusy.Visible:
			xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
			DialogBusy.Visible = True

	@staticmethod
	def Close():
		if DialogBusy.Visible:
			xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
			DialogBusy.Visible = False

# if __name__ == '__main__':
# 	if len(sys.argv) >= 2:
# 		file = sys.argv[1]
# 		xbmc.log(file,level=xbmc.LOGINFO) 
# 	else:
# 		file = os.path.join(__addonpath__,'markdown-cheat-sheet.md')
# 	d=UserGuide('userguide.xml',__addonpath__,'Default','720p',mdfile=file)
# 	d.doModal()
# 	del d