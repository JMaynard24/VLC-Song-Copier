import requests
import sys
from shutil import copy2
import keyboard
from urllib.request import unquote
import tkinter.filedialog
import os
from os.path import isfile
import socket
from contextlib import closing
import configparser
from time import sleep
from tkinter import Tk


# -----------------------------------------------------------------------------


def check_socket(host, port):
    """Warns user if port is not open."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) != 0:
            print()
            print("Port is not open, either VLC isn't open or there was a problem opening your port.")
            portClosed = input("Would you like to continue anyway (y/n)? ")
            while portClosed != "y" and portClosed != "Y" and portClosed != "n" and portClosed != "N":
                portClosed = input('Sorry, only y/n allowed! Try again: ')
            if portClosed == "y" or portClosed == "Y":
                print('Understood, continuing anyway.')
            elif portClosed == "n" or portClosed == "N":
                sys.exit()
            print()


# -----------------------------------------------------------------------------


def vlcxml(page):
    """Grabs the xml needed from VLC's HTTP server."""
    s = requests.Session()
    s.auth = ('', pswrd)  # Username is blank, just provide the password
    r = s.get('http://localhost:' + port + '/requests/' + str(page) + '.xml', verify=False)
    return r.text


# -----------------------------------------------------------------------------


def is_number(num):
    """Given string 'num', returns true if 'num' is numeric."""
    try:
        int(num)
        return True
    except ValueError:
        return False


# -----------------------------------------------------------------------------


def fixName(t):
    """Given string 't', returns a filtered version."""
    return (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            .replace("&#39;", "'").replace('&quot;', '"'))


# -----------------------------------------------------------------------------


def copyFile():
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
        newFile = (dirname + fileName)
        extensionStart = fileName.rfind('.')
        extension = fileName[extensionStart:]

        if isfile(newFile) is False:
            copy2(convertURL, dirname)
            print()
            print('Successfully copied ' + convertURL + ' to ' + dirname)
            renameResponse = reName()
            if renameResponse is not None:
                os.rename(newFile, (dirname + '/' + renameResponse + extension))
                print('Successfully renamed your file!')
        elif overwriteAlways == "n" or overwriteAlways == "N":
            print()
            overwrite = input('That file already exists, would you like to overwrite it (y/n)? ')
            while overwrite != "y" and overwrite != "Y" and overwrite != "n" and overwrite != "N":
                overwrite = input('Sorry, only y/n allowed! Try again: ')
            if overwrite == "y" or overwrite == "Y":
                copy2(convertURL, dirname)
                print()
                print('Successfully overwritten ' + newFile)
                renameResponse = reName()
                if renameResponse is not None:
                    if isfile((dirname + '/' + renameResponse + extension)) is False:
                        os.rename(newFile, (dirname + '/' + renameResponse + extension))
                        print('Successfully renamed your file!')
                    else:
                        print('Sorry, file with that name already existed! Aborting rename.')
            elif overwrite == "n" or overwrite == "N":
                print('Understood, copy canceled.')
        elif overwriteAlways == "y" or overwriteAlways == "Y":
            copy2(convertURL, dirname)
            print()
            print('Successfully copied ' + convertURL + ' to ' + dirname)
            print('Due to your settings, this file was automatically overwritten!')
            renameResponse = reName()
            if renameResponse is not None:
                os.rename(newFile, (dirname + '/' + renameResponse + extension))
                print('Successfully renamed your file!')


# -----------------------------------------------------------------------------


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
    if renameMethod == "7":
        print()
        response = input('Would you like to rename your new file (y/n)? ')
        while response != "y" and response != "Y" and response != "n" and response != "N":
            response = input('Sorry, only y/n allowed! Try again: ')
        if response == "y" or response == "Y":
            print()
            print('Here are your options for renaming!')
            print()
            print('    --> 1.  ' + artist + ' - ' + title)
            print('    --> 2.  ' + album + ' - ' + title)
            print('    --> 3.  ' + artist + ' - ' + album + ' - ' + title)
            print('    --> 4.  ' + album + ' - ' + artist + ' - ' + title)
            print('    --> 5.  ' + title)
            print('    --> 6.  Manual Renaming')
            print()
            answer = input('What is your choice (1-6)? ')
            while is_number(answer) is False or int(answer) > 6 or int(answer) < 1:
                answer = input('Sorry, only 1-6 allowed. Try again: ')
            if answer == "1":
                return str(artist + ' - ' + title)
            elif answer == "2":
                return str(album + ' - ' + title)
            elif answer == "3":
                return str(artist + ' - ' + album + ' - ' + title)
            elif answer == "4":
                return str(album + ' - ' + artist + ' - ' + title)
            elif answer == "5":
                return str(title)
            elif answer == "6":
                newName = input('Please input your new filename without extension: ')
                return str(newName)
        elif response == "n" or response == "N":
            print('Okay, press "' + copyhotkey + '" when you would like to copy the next song!')
    elif int(renameMethod) > 0 and int(renameMethod) < 7:
        if renameMethod == "1":
            return str(artist + ' - ' + title)
        elif renameMethod == "2":
            return str(album + ' - ' + title)
        elif renameMethod == "3":
            return str(artist + ' - ' + album + ' - ' + title)
        elif renameMethod == "4":
            return str(album + ' - ' + artist + ' - ' + title)
        elif renameMethod == "5":
            return str(title)
        elif renameMethod == "6":
            newName = input('Please input your new filename without extension: ')
            return str(newName)
    elif renameMethod == "8":
        return None


# -----------------------------------------------------------------------------


sys.path.append('..')

print('This small program will read the currently playing song from VLC and copy it to a folder of your choosing.')
print('Great for easily making playlists from large libraries!')
print()
print()
print('Before you can use this program you need to make sure you have a few settings set correctly in VLC.')
print('Make sure you pick "All" for "Show Settings" in the bottom left of your Preferences')
print('First check the "Web" box at Tools -> Preferences -> Interface -> Main interfaces')
print('Next set your password at Tools -> Preferences -> Interface -> Main interfaces -> Lua -> Lua HTTP')
print('Finally, go to Tools -> Preferences -> Input / Codecs and scroll down to Network Settings and set your "HTTP Server Port"')
print('Save your settings and restart VLC and you should be good to go!')
print()
print("Make sure VLC is open if you want your port to be checked!")
print()

Config = configparser.ConfigParser()

if isfile('settings.ini') is True:
    Config.read('settings.ini')
    print('Loading settings from settings.ini')
    pswrd = Config.get('Settings', 'vlc password')
    port = Config.get('Settings', 'vlc http port')
    renameMethod = Config.get('Settings', 'renaming method')
    dirname = Config.get('Settings', 'new directory')
    overwriteAlways = Config.get('Settings', 'overwritealways')
    copyhotkey = Config.get('Settings', 'copy hotkey')
    Config.remove_section('Settings')
    print()
    print('Here are your current settings:')
    print(' VLC Password = ' + pswrd)
    print(' VLC HTTP Port = ' + port)
    print(' Renaming Method = ' + renameMethod)
    print(' New Directory = ' + dirname)
    print(' Overwrite Always = ' + overwriteAlways)
    print(' Copy Hotkey = ' + copyhotkey)
    print()
    contSettings = input('Continue with those settings y/n? ')
    while contSettings != "y" and contSettings != "Y" and contSettings != "n" and contSettings != "N":
        contSettings = input('Sorry, only y/n allowed! Try again: ')
    if contSettings == "n" or contSettings == "N":
        print('Okay, will run through the settings again.')
        print()
    else:
        print()


if isfile('settings.ini') is False or contSettings == "n" or contSettings == "N":
    pswrd = input('What is your VLC server password? ')

    port = input('Enter the HTTP Server Port: ')
    while is_number(port) is False or int(port) < 1:
        port = input('Only positive numbers allowed! Try again: ')

    check_socket('127.0.0.1', int(port))

    overwriteAlways = input('Would you like to either always overwrite when copying (y/n)? ')
    while overwriteAlways != "y" and overwriteAlways != "Y" and overwriteAlways != "n" and overwriteAlways != "N":
        overwriteAlways = input('Sorry, only y/n allowed! Try again: ')

    print()
    print('Choose how you would like to rename your new files.')
    print()
    print('    --> 1.  Artist - Title')
    print('    --> 2.  Album - Title')
    print('    --> 3.  Artist - Album - Title')
    print('    --> 4.  Album - Artist - Title')
    print('    --> 5.  Title')
    print('    --> 6.  Manual Renaming')
    print('    --> 7.  Choose per file')
    print('    --> 8.  Skip renaming')
    print()
    renameMethod = input('What is your choice? (1-8): ')
    while is_number(renameMethod) is False or int(renameMethod) > 8 or int(renameMethod) < 1:
        renameMethod = input('Sorry, only numbers 1-8 allowed! Try again: ')

    print()
    sleep(1)
    print('Please press a key to be the hotkey for copying.')
    hotkey = str(keyboard.read_key())
    end = hotkey.rfind(' down')
    copyhotkey = hotkey[14:end]
    print('You chose: ' + copyhotkey)
    print()

    print('Please choose the directory you\'d like to copy to')
    root = Tk()
    root.withdraw()
    dirname = tkinter.filedialog.askdirectory(parent=root, initialdir="/", title='Choose a directory to copy to')
    while dirname == "":
        print('You did not enter a directory, please try again.')
        dirname = tkinter.filedialog.askdirectory(parent=root, initialdir="/", title='Choose a directory to copy to')

    print('You chose: ' + dirname)
    print()

    settingscheck = input("Would you like to save your settings so far so you don't have to put them in next time (y/n)? ")
    while settingscheck != "y" and settingscheck != "Y" and settingscheck != "n" and settingscheck != "N":
        settingscheck = input('Sorry, only y/n allowed! Try again: ')
    if settingscheck == "y" or settingscheck == "Y":
        if isfile('settings.ini'):
            os.remove('settings.ini')
            sleep(1)
        cfgfile = open("settings.ini", 'a+')
        Config.add_section('Settings')
        Config.set('Settings', 'vlc password', pswrd)
        Config.set('Settings', 'vlc http port', port)
        Config.set('Settings', 'renaming method', renameMethod)
        Config.set('Settings', 'new directory', dirname)
        Config.set('Settings', 'overwritealways', overwriteAlways)
        Config.set('Settings', 'copy hotkey', copyhotkey)
        Config.write(cfgfile)
        cfgfile.close()
    else:
        print('Okay, not saving.')

print()
print('Whenever you press "' + copyhotkey + '", you will now copy the currently playing song to your new directory!')
print('You can do this as many times as you like, even if you close and reopen VLC!')

keyboard.add_hotkey(copyhotkey, copyFile)
keyboard.wait()
