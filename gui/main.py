#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import urllib2, urllib #login, open page, etc. 
import re #regexp
import cookielib #use cookie
# Import Qt modules
from PyQt4 import QtCore,QtGui

# Import the compiled UI module
from ui_synchvk import Ui_MainWindow

# Create a class for our main window
class Main(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
         # This is always the same
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.do_it)
         

    def LoginVk(self,email,password):
        self.ui.statusbar.showMessage('Connect to Vk...')
        url = "http://login.vk.com?"
        form_data = {'act' : 'login', 'q' : '1', 'al_frame' : '1',
                 'expire' : '', 'captcha_sid' : '',  'captcha_key' : '','from_host' : 'vkontakte.ru',
                 'email' : email, 'pass' : password} 
    
        jar = cookielib.CookieJar() #cookie storage
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar)) #opener whith cookie
        
        form_data = urllib.urlencode(form_data) # encode url data
        check=0
        try:
            resp = opener.open(url, form_data)  # login
        except:
            check=1
        try:
            resp = opener.open('http://vkontakte.ru/audio')  #open audio page
        except:
            check=1

        if check:
            response=1
        else:
            response=resp.read() #copy response
            resp.close() #close site
            response = response.decode('cp1251') # decode windows-1251
            self.ui.statusbar.showMessage('Connected')
        
        return response


    def DownloaderMp3(self,url,artist,song):
        file_name = artist+' - '+song+'.mp3'
        self.ui.label_3.setText('Downloading: %s' % (file_name))
        file_name = 'music/'+file_name
        if os.path.isfile(file_name):
            self.ui.statusbar.showMessage('file exists')
        else:        
            u = urllib2.urlopen(url)            
            f = open(file_name, 'wb')
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            self.ui.statusbar.showMessage('Bytes: %s' % (file_size))

            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                file_size_dl += block_sz
                f.write(buffer)
                self.ui.progressBar.setValue(file_size_dl * 100/file_size)                
            f.close()
            self.ui.statusbar.showMessage('Done')

    def do_it(self):
        page=self.LoginVk(str(self.ui.lineEdit.text()),str(self.ui.lineEdit_2.text()))#login and password
        if page==1 :
            self.ui.statusbar.showMessage('connection problem')
        else:            
            artist_list = re.findall(r'; return false">(.*)</a></b>',page) #take name of artist
            del artist_list[-1] # delete '+audio[5]+' 
            song_list = re.findall(r'</b> - <span class="title">(.*) </span>',page) #take name of song
            del song_list[-1] # delete '+lyricsLink+' 
            mp3_list = re.findall(r'value="(http://.*mp3),\d*"',page) #take url mp3 file
    
            ###########clearing song_list#########
            i=0
            for item in song_list:
                if re.match('.*</a>', item):
                    clear = re.findall(r'">(.*)</a>',item)
                    song_list[i]=clear[0]
                i+=1
            ###################################

            if not os.path.exists('music/'):
                os.mkdir("music", 0770)
                

            playlist_name = 'music/vkplaylist.m3u' #name playlist
            f = open(playlist_name, 'w') #create playlist
            
            i=0
            while i<len(mp3_list):
                self.DownloaderMp3(mp3_list[i],artist_list[i],song_list[i]) #Download mp3
                line_list = artist_list[i]+' - '+song_list[i]+'.mp3\n' #one line in playlist file
                f.write(line_list.encode("utf8")) #save line in playlist file
                i+=1
            f.close() #Close playlist file

            self.ui.statusbar.showMessage('Finish')




def main():
    # Again, this is boilerplate, it's going to be the same on
    # almost every app you write
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

    
