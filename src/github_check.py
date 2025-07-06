import requests
git_link= 'https://github.com/AndreAR22/kinito-downloader/releases/latest'
response = requests.get(git_link)
git_version = response.url.split('/').pop()
local_version = 'v2.1'

from tkinter import *
root = Tk()
import os
import pygame

EXE_LOCATION = os.path.dirname(os.path.realpath(__file__))

def open_project(warn):
    root.destroy()
    if warn == 1:
        pygame.mixer.Sound(os.path.join(EXE_LOCATION, 'no_tanks.mp3')).play()
    import main

if git_version <= local_version:
    open_project(0)
else:
    pygame.mixer.init()
    # the kid was killed :33
    os.system("start "+str(git_link))
    Label(root, text="Download the latest version!!!11").pack()
    button = Button(root, text="no xdd fuck u", command=lambda: open_project(1)).pack()
    root.mainloop()
