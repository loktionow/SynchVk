#!/usr/bin/env python
#
#
import urllib2, urllib #login, open page, etc. 
import re #regexp
import cookielib #use cookie
import os.path

def LoginVk(email,password):
    print 'Connect to Vk...'
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
        print 'Done'
    return response


def DownloaderMp3(url,artist,song):
    file_name = artist+' - '+song+'.mp3'
    print "Downloading: %s" % (file_name)
    if os.path.isfile(file_name):
        print 'file exists'
    else:        
        u = urllib2.urlopen(url)
        file_name = 'music/'+file_name
        f = open(file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Bytes: %s" % (file_size)

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += block_sz
            f.write(buffer)
            #status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            #status = status + chr(8)*(len(status)+1)
            #print status,    
        f.close()
        print 'Done'

def main():
    page=LoginVk('You@mail.com','youpassword')#login and password
    if page==1 :
        print'connection problem'
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

        if not os.path.isfile('music/'):
            os.mkdir("music", 0770)

        playlist_name = 'music/vkplaylist.m3u' #name playlist
        f = open(playlist_name, 'w') #create playlist
            
        i=0
        while i<len(mp3_list):
            DownloaderMp3(mp3_list[i],artist_list[i],song_list[i]) #Download mp3
            line_list = artist_list[i]+' - '+song_list[i]+'.mp3\n' #one line in playlist file
            f.write(line_list.encode("utf8")) #save line in playlist file
            i+=1
        f.close() #Close playlist file

        print 'Finish'
 

if __name__=='__main__':

    main()
