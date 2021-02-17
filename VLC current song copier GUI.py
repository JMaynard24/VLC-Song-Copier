import requests
import sys
from shutil import copy2
import keyboard
from urllib.request import unquote
import tkinter.filedialog
import os
from os.path import isfile
import configparser
import time
from tkinter import Label, Button, Entry, Checkbutton, Tk, Toplevel, BooleanVar, PhotoImage, font
from tkinter.ttk import Separator, Style
import tkinter.messagebox
from ReadWriteMemory import rwm
from contextlib import closing
import socket

# -----------------------------------------------------------------------------


class MainWin:

    def __init__(self, parent):

        def Help():
            t = Toplevel()
            t.title("Help")

            t.label = Label(t, text='This small program will read the currently playing song from VLC and copy it to a folder of your choosing.')
            t.label.pack()
            t.label2 = Label(t, text='Great for easily making playlists from large libraries!')
            t.label2.pack()
            t.label3 = Label(t, text='')
            t.label3.pack()
            t.label4 = Label(t, text='')
            t.label4.pack()
            t.label5 = Label(t, text='Before you can use this program you need to make sure you have a few settings set correctly in VLC.')
            t.label5.pack()
            t.label6 = Label(t, text='Make sure you pick "All" for "Show Settings" in the bottom left of your Preferences')
            t.label6.pack()
            t.label7 = Label(t, text='First check the "Web" box at Tools -> Preferences -> Interface -> Main interfaces')
            t.label7.pack()
            t.label8 = Label(t, text='Next set your password at Tools -> Preferences -> Interface -> Main interfaces -> Lua -> Lua HTTP')
            t.label8.pack()
            t.label9 = Label(t, text='Finally, go to Tools -> Preferences -> Input / Codecs and scroll down to Network Settings and set your "HTTP Server Port"')
            t.label9.pack()
            t.label10 = Label(t, text='Save your settings and restart VLC and you should be good to go!')
            t.label10.pack()

        def Browse(root):
            root.withdraw()
            self.dirname = tkinter.filedialog.askdirectory(parent=root, initialdir="/", title='Choose a directory to copy to')
            return self.dirname

        def CheckPort(host, port):
            """Warns user if port is not open."""
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                if sock.connect_ex((host, port)) != 0:
                    tkinter.messagebox.showinfo('Error', 'Either VLC or the Port is not open!')
                    self.startConnection.set(False)
                    return False
                else:
                    return True

        def ReadSettings():
            Config = configparser.ConfigParser()
            if isfile('settings.ini') is True:
                Config.read('settings.ini')
                self.pswrd = Config.get('Settings', 'vlc password')
                self.port = Config.get('Settings', 'vlc http port')
                self.renameMethod = Config.get('Settings', 'renaming method')
                self.dirname = Config.get('Settings', 'new directory')
                self.overwriteAlways.set(Config.getboolean('Settings', 'overwrite always'))
                self.copyhotkey = Config.get('Settings', 'copy hotkey')
                Config.remove_section('Settings')
                return self.pswrd, self.port, self.renameMethod, self.dirname, self.overwriteAlways, self.copyhotkey

        def SaveSettings(pswrd, port, renameMethod, dirname, overwriteAlways, copyhotkey):
            Config = configparser.ConfigParser()
            cfgfile = open("settings.temp.ini", 'w+')
            Config.add_section('Settings')
            Config.set('Settings', 'vlc password', self.pswrd)
            Config.set('Settings', 'vlc http port', self.port)
            Config.set('Settings', 'renaming method', self.renameMethod)
            Config.set('Settings', 'new directory', self.dirname)
            Config.set('Settings', 'activate hotkey', str(self.activateHotkey.get()))
            Config.set('Settings', 'overwrite always', str(self.overwriteAlways.get()))
            Config.set('Settings', 'copy hotkey', self.copyhotkey)
            Config.write(cfgfile)
            time.sleep(.1)
            if isfile('settings.ini'):
                os.remove('settings.ini')
            cfgfile.close()
            os.rename('settings.temp.ini', 'settings.ini')

        def SetServerPass():
            self.pswrd = self.PassEntry.get()
            return self.pswrd

        def SetServerPort():
            if is_number(self.PortEntry.get()) is True:
                self.port = self.PortEntry.get()
                return self.port
            else:
                tkinter.messagebox.showinfo('Error', 'Only numbers allowed!')

        def SetRenameMethod():
            if is_number(self.SetRenameEntry.get()) is False or int(self.SetRenameEntry.get()) > 6 or int(self.SetRenameEntry.get()) < 1:
                tkinter.messagebox.showinfo('Error', 'Only numbers 1-6 allowed!')
            else:
                self.renameMethod = self.SetRenameEntry.get()
                return self.renameMethod

        def SetHotkey():
            hotkey = str(keyboard.read_key())
            end = hotkey.rfind(' down')
            self.copyhotkey = hotkey[14:end]

            t = Toplevel()
            t.title("New Hotkey")
            t.label = Label(t, text='You chose: ' + self.copyhotkey)
            t.label.pack()
            return self.copyhotkey

        def CheckSettings():
            if is_number(self.renameMethod) is True and int(self.renameMethod) > 0 and int(self.renameMethod) < 7:
                if is_number(self.port) is True:
                    if self.pswrd != '':
                        if self.dirname != '':
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False

        def CheckVLC():
            check = rwm.OpenProcess('vlc.exe')
            if check is not None:
                return 'Opened!'
            else:
                self.startConnection.set(False)
                return 'Not Open'

        def RenameMethods():
            t = Toplevel()
            t.title("Rename Methods")
            t.label = Label(t, text='Here are your options for renaming!')
            t.label.pack()
            t.label2 = Label(t, text='1. Artist - Title')
            t.label2.pack()
            t.label3 = Label(t, text='2. Album - Title')
            t.label3.pack()
            t.label4 = Label(t, text='3. Artist - Album - Title')
            t.label4.pack()
            t.label5 = Label(t, text='4. Album - Artist - Title')
            t.label5.pack()
            t.label6 = Label(t, text='5. Title')
            t.label6.pack()
            t.label7 = Label(t, text='6. Don\'t Rename')
            t.label7.pack()

        def CurrentSong():
            """When called, grabs info from VLC to rename the new file."""
            status = vlcxml('status')
            if status is not None:
                startTitle = status.find("<info name='title'>")
                startArtist = status.find("<info name='artist'>")
                startAlbum = status.find("<info name='album'>")
                startStatus = status.find("<state>")
                fromstartTitle = status[startTitle:]
                fromstartArtist = status[startArtist:]
                fromstartAlbum = status[startAlbum:]
                fromstartStatus = status[startStatus:]
                endTitle = fromstartTitle.find("</info>")
                endArtist = fromstartArtist.find("</info>")
                endAlbum = fromstartAlbum.find("</info>")
                endStatus = fromstartStatus.find("</state>")
                title = fixName(fromstartTitle[19:endTitle])
                artist = fixName(fromstartArtist[20:endArtist])
                album = fixName(fromstartAlbum[19:endAlbum])
                status = fixName(fromstartStatus[7:endStatus])
                self.currentstatus = (status[0].upper() + status[1:])
                if (artist + " - " + album + ' - ' + title) == " -  - ":
                    self.currentsong = 'No info available'
                    self.currentartist = 'No info available'
                    self.currentalbum = 'No info available'
                    self.currenttitle = 'No info available'
                else:
                    self.currentsong = (artist + " - " + album + ' - ' + title)
                    self.currentartist = artist
                    self.currentalbum = album
                    self.currenttitle = title
            else:
                return None

        def vlcxml(page):
            if self.startConnection.get() is True:
                """Grabs the xml needed from VLC's HTTP server."""
                s = requests.Session()
                s.auth = ('', self.pswrd)  # Username is blank, just provide the password
                try:
                    r = s.get('http://localhost:' + self.port + '/requests/' + str(page) + '.xml', verify=False)
                    return r.text
                except requests.exceptions.RequestException as e:
                    self.startConnection.set(False)
                    tkinter.messagebox.showinfo('Error', 'Something went wrong! Check your settings and make sure VLC is open! \n\n' + str(e))
                    return None
            else:
                return None

        def is_number(num):
            """Given string 'num', returns true if 'num' is numeric."""
            try:
                int(num)
                return True
            except ValueError:
                return False

        def fixName(t):
            """Given string 't', returns a filtered version."""
            while t != (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                         .replace("&#39;", "'").replace('&quot;', '"')):
                t = (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                     .replace("&#39;", "'").replace('&quot;', '"'))
            return t

        def copyFile():
            if CheckSettings() is True and CheckPort('127.0.0.1', int(self.port)) is True:
                """When called, grabs info from VLC to copy file to new path."""
                x1 = vlcxml('status')
                start = x1.find('<currentplid>')
                end = x1.find('</currentplid>')
                plid = x1[start + 13:end]

                if plid is not None:
                    x2 = vlcxml('playlist')
                    start2 = x2.find('id="' + plid + '" duration=')
                    fromStart = x2[start2:]
                    start3 = fromStart.find('uri=')
                    end2 = fromStart.find('/>')
                    start3 = fromStart.find('uri=')
                    end2 = fromStart.find('/>')
                    filePath = fromStart[start3 + 13:end2 - 19]

                    bugstart = x2.find(filePath)  # Getting around VLC bug block
                    bug1 = x2[bugstart:]
                    bugend = bug1.find('/>')
                    bugFixin = x2[:(bugstart + bugend)]
                    bugg = bugFixin.count('vlc://nop')
                    if bugg > 0:
                        plid = str(int(plid) + bugg)
                        start2 = x2.find('id="' + plid + '" duration=')
                        fromStart = x2[start2:]
                        start3 = fromStart.find('uri=')
                        end2 = fromStart.find('/>')
                        filePath = fromStart[start3 + 13:end2 - 1]  # Bug block end

                    convertURL = unquote(filePath)
                    fileNameStart = convertURL.rfind('/')
                    fileName = convertURL[fileNameStart:]
                    newFile = (self.dirname + fileName)
                    extensionStart = fileName.rfind('.')
                    extension = fileName[extensionStart:]
                    self.localtime = time.strftime("%H:%M:%S", time.localtime())

                    time.sleep(.1)
                    try:
                        if isfile(newFile) is True:
                            if self.overwriteAlways.get() is True:
                                os.remove(newFile)
                                renameResponse = reName()
                                if renameResponse is not None:
                                    if isfile(self.dirname + '/' + renameResponse + extension) is True:
                                        if self.overwriteAlways.get() is True:
                                            os.remove(self.dirname + '/' + renameResponse + extension)
                                            copy2(convertURL, self.dirname)
                                            os.rename(newFile, (self.dirname + '/' + renameResponse + extension))
                                            self.ProgStatusVarLabel.config(text='Successful Overwrite at ' + self.localtime)
                                        else:
                                            self.ProgStatusVarLabel.config(text='File Already Exists! ' + self.localtime)
                                    else:
                                        copy2(convertURL, self.dirname)
                                        os.rename(newFile, (self.dirname + '/' + renameResponse + extension))
                                        self.ProgStatusVarLabel.config(text='Successful Overwrite at ' + self.localtime)
                                else:
                                    copy2(convertURL, self.dirname)
                                    self.ProgStatusVarLabel.config(text='Successful Copy at ' + self.localtime)
                            else:
                                self.ProgStatusVarLabel.config(text='File Already Exists! ' + self.localtime)
                        else:
                            renameResponse = reName()
                            if renameResponse is not None:
                                if isfile(self.dirname + '/' + renameResponse + extension) is True:
                                    if self.overwriteAlways.get() is True:
                                        os.remove(self.dirname + '/' + renameResponse + extension)
                                        copy2(convertURL, self.dirname)
                                        os.rename(newFile, (self.dirname + '/' + renameResponse + extension))
                                        self.ProgStatusVarLabel.config(text='Successful Overwrite at ' + self.localtime)
                                    else:
                                        self.ProgStatusVarLabel.config(text='File Already Exists! ' + self.localtime)
                                else:
                                    copy2(convertURL, self.dirname)
                                    os.rename(newFile, (self.dirname + '/' + renameResponse + extension))
                                    self.ProgStatusVarLabel.config(text='Successful Copy at ' + self.localtime)
                            else:
                                copy2(convertURL, self.dirname)
                                self.ProgStatusVarLabel.config(text='Successful Copy at ' + self.localtime)
                    except PermissionError:
                        self.ProgStatusVarLabel.config(text="File in use! Can't Delete " + self.localtime)
            elif CheckSettings() is False:
                tkinter.messagebox.showinfo('Error', 'Settings not correct, check your settings!')
                self.startConnection.set(False)

        def reName():
            """When called, grabs info from VLC to rename the new file."""
            status = vlcxml('status')
            startTitle = status.find("<info name='title'>")
            startArtist = status.find("<info name='artist'>")
            startAlbum = status.find("<info name='album'>")
            fromstartTitle = status[startTitle:]
            fromstartArtist = status[startArtist:]
            fromstartAlbum = status[startAlbum:]
            endTitle = fromstartTitle.find("</info>")
            endArtist = fromstartArtist.find("</info>")
            endAlbum = fromstartAlbum.find("</info>")
            title = fixName(fromstartTitle[19:endTitle])
            artist = fixName(fromstartArtist[20:endArtist])
            album = fixName(fromstartAlbum[19:endAlbum])
            if int(self.renameMethod) > 0 and int(self.renameMethod) < 7:
                if self.renameMethod == "1":
                    return str(artist + ' - ' + title)
                elif self.renameMethod == "2":
                    return str(album + ' - ' + title)
                elif self.renameMethod == "3":
                    return str(artist + ' - ' + album + ' - ' + title)
                elif self.renameMethod == "4":
                    return str(album + ' - ' + artist + ' - ' + title)
                elif self.renameMethod == "5":
                    return str(title)
            elif self.renameMethod == "6":
                return None

        def HotKeyBind():
            if self.activateHotkey.get() is True:
                keyboard.add_hotkey(self.copyhotkey, copyFile)
            else:
                keyboard.clear_all_hotkeys()

    # Variables
        self.pswrd = ''
        self.port = ''
        self.renameMethod = '6'
        self.dirname = ''
        self.activateHotkey = BooleanVar()
        self.overwriteAlways = BooleanVar()
        self.startConnection = BooleanVar()
        self.copyhotkey = ''
        ReadSettings()
        self.currentsong = 'Nothing Playing!'
        self.currentartist = 'Nothing Playing!'
        self.currentalbum = 'Nothing Playing!'
        self.currenttitle = 'Nothing Playing!'
        self.currentstatus = 'Not Open'

        self.photo = PhotoImage(file='vlc banner.png')
        self.photo_label = Label(image=self.photo)
        self.photo_label.place(x=0, y=0)
        self.photo_label.image = self.photo

        self.seperator = Separator(parent, orient="horizontal")
        self.seperator.place(relwidth=1.0, y=131)
        Style().configure(self.seperator, background='#000')

        self.PassLabel = Label(parent, text='Vlc Server Password:', font=('Times', 12),
                               fg='black')
        self.PassLabel.place(x=5, y=145)

        self.PortLabel = Label(parent, text='Vlc Server Port:', font=('Times', 12),
                               fg='black')
        self.PortLabel.place(x=40, y=195)

        self.RenMethLabel = Label(parent, text='Rename Method:', font=('Times', 12),
                                  fg='black')
        self.RenMethLabel.place(x=30, y=245)

        self.DirLabel = Label(parent, text='New Directory:', font=('Times', 12),
                              fg='black')
        self.DirLabel.place(x=8, y=280)

        self.VLCStatusLabel = Label(parent, text='VLC Status:', font=('Times', 12),
                                    fg='black')
        self.VLCStatusLabel.place(x=27, y=305)

        self.ProgStatusLabel = Label(parent, text='Last Action:', font=('Times', 12),
                                     fg='black')
        self.ProgStatusLabel.place(x=27, y=330)

        self.CurrentSongLabel = Label(parent, text=('Current Song'), font=('Times', 12),
                                      fg='black')
        self.CurrentSongLabel.place(x=50, y=360)

        f = font.Font(self.CurrentSongLabel, self.CurrentSongLabel.cget("font"))
        f.configure(underline=True)
        self.CurrentSongLabel.configure(font=f)

        self.CurrentArtistLabel = Label(parent, text='Artist:', font=('Times', 12),
                                        fg='black')
        self.CurrentArtistLabel.place(x=17, y=385)

        self.CurrentAlbumLabel = Label(parent, text='Album:', font=('Times', 12),
                                       fg='black')
        self.CurrentAlbumLabel.place(x=10, y=410)

        self.CurrentTitleLabel = Label(parent, text='Title:', font=('Times', 12),
                                       fg='black')
        self.CurrentTitleLabel.place(x=24, y=435)

        self.PassVarLabel = Label(parent, text=self.pswrd, font=('Times', 12),
                                  fg='black')
        self.PassVarLabel.place(x=140, y=145)

        self.PortVarLabel = Label(parent, text=self.port, font=('Times', 12),
                                  fg='black')
        self.PortVarLabel.place(x=140, y=195)

        self.RenMethVarLabel = Label(parent, text=self.renameMethod, font=('Times', 12),
                                     fg='black')
        self.RenMethVarLabel.place(x=140, y=245)

        self.DirVarLabel = Label(parent, text=self.dirname, font=('Times', 12),
                                 fg='black')
        self.DirVarLabel.place(x=105, y=280)

        self.VLCStatusVarLabel = Label(parent, text='Not Open', font=('Times', 12),
                                       fg='black')
        self.VLCStatusVarLabel.place(x=105, y=305)

        self.ProgStatusVarLabel = Label(parent, text='Nothing yet!', font=('Times', 12),
                                        fg='black')
        self.ProgStatusVarLabel.place(x=105, y=330)

        self.CurrentArtistVarLabel = Label(parent, text=self.currentartist, font=('Times', 12),
                                           fg='black')
        self.CurrentArtistVarLabel.place(x=60, y=385)

        self.CurrentAlbumVarLabel = Label(parent, text=self.currentalbum, font=('Times', 12),
                                          fg='black')
        self.CurrentAlbumVarLabel.place(x=60, y=410)

        self.CurrentTitleVarLabel = Label(parent, text=self.currenttitle, font=('Times', 12),
                                          fg='black')
        self.CurrentTitleVarLabel.place(x=60, y=435)

        self.PassEntry = Entry(parent)
        self.PassEntry.place(w=120, h=35, x=240, y=140)

        self.PortEntry = Entry(parent)
        self.PortEntry.place(w=120, h=35, x=240, y=190)

        self.SetRenameEntry = Entry(parent)
        self.SetRenameEntry.place(w=120, h=35, x=240, y=240)

        def Refresh():
            CurrentSong()
            self.PassVarLabel.config(text=self.pswrd)
            self.PortVarLabel.config(text=self.port)
            self.RenMethVarLabel.config(text=self.renameMethod)
            self.DirVarLabel.config(text=self.dirname)
            if self.startConnection.get() is False:
                self.CurrentArtistVarLabel.config(text='Start Connection to get info!')
                self.CurrentAlbumVarLabel.config(text='Start Connection to get info!')
                self.CurrentTitleVarLabel.config(text='Start Connection to get info!')
                self.VLCStatusVarLabel.config(text=CheckVLC())
            else:
                self.CurrentArtistVarLabel.config(text=self.currentartist)
                self.CurrentAlbumVarLabel.config(text=self.currentalbum)
                self.CurrentTitleVarLabel.config(text=self.currenttitle)
                self.VLCStatusVarLabel.config(text=self.currentstatus)
            parent.after(500, Refresh)

        self.PassButton = Button(parent, text='Set', command=SetServerPass, font=('Times', 10))
        self.PassButton.place(w=120, h=35, x=380, y=140)

        self.PortButton = Button(parent, text='Set', command=SetServerPort, font=('Times', 10))
        self.PortButton.place(w=120, h=35, x=380, y=190)

        self.SetRenameButton = Button(parent, text='Set', command=SetRenameMethod, font=('Times', 10))
        self.SetRenameButton.place(w=120, h=35, x=380, y=240)

        self.BrowseButton = Button(parent, text='Browse', command=lambda: Browse(Tk()), font=('Times', 10))
        self.BrowseButton.place(w=120, h=35, x=570, y=290)

        self.SetHotkeyButton = Button(parent, text='Set Hotkey', command=SetHotkey, font=('Times', 10))
        self.SetHotkeyButton.place(w=120, h=35, x=570, y=340)

        self.CopyButton = Button(parent, text='Copy File', command=copyFile, font=('Times', 10))
        self.CopyButton.place(w=120, h=35, x=570, y=425)

        self.HelpButton = Button(parent, text='Setup', command=Help, font=('Times', 10))
        self.HelpButton.place(w=120, h=35, x=570, y=140)

        self.HelpButton = Button(parent, text='Save Settings', command=lambda: SaveSettings(self.pswrd, self.port, self.renameMethod, self.dirname, self.overwriteAlways, self.copyhotkey), font=('Times', 10))
        self.HelpButton.place(w=120, h=35, x=570, y=190)

        self.RenameMethodsButton = Button(parent, text='Renaming Methods', command=RenameMethods, font=('Times', 10))
        self.RenameMethodsButton.place(w=120, h=35, x=570, y=240)

        self.ActivHotkeyCheckbox = Checkbutton(parent, text='Activate Hotkey', variable=self.activateHotkey, command=HotKeyBind, font=('Times', 10))
        self.ActivHotkeyCheckbox.place(x=420, y=310)

        self.OvrAlwCheckbox = Checkbutton(parent, text='Overwrite New Files', variable=self.overwriteAlways, font=('Times', 10))
        self.OvrAlwCheckbox.place(x=420, y=330)

        self.StartConCheckbox = Checkbutton(parent, text='Start Connection', variable=self.startConnection, font=('Times', 10))
        self.StartConCheckbox.place(x=420, y=350)

        Refresh()

# -----------------------------------------------------------------------------


def main():
    global MainWindow
    root = Tk()
    wFilter = 700
    hFilter = 470
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - wFilter) / 2
    y = (sh - hFilter) / 2
    root.geometry('%dx%d+%d+%d' % (wFilter, hFilter, x, y))
    root.resizable(width=False, height=False)
    root.title('VLC Current Song Copier')

    MainWindow = MainWin(root)
    root.mainloop()
    sys.exit(1)


if __name__ == '__main__':
    main()
