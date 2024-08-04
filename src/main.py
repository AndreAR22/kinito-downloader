from tkinter import *
from PIL import ImageTk, Image
import os
import winreg

# Fetch the Downloads folder path
reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
downloads = winreg.QueryValueEx(reg_key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
winreg.CloseKey(reg_key)

EXE_LOCATION = os.path.dirname(os.path.realpath(__file__))
airy1 = Image.open(os.path.join(EXE_LOCATION, "kinito1.png"))
airy2 = os.path.join(EXE_LOCATION, "kinito2.ico")
airy1 = airy1.resize((int(airy1.width / 3), int(airy1.height / 3)))

img_mp4 = Image.open(os.path.join(EXE_LOCATION, "button_mp4.png"))
img_mp4 = img_mp4.resize((int(img_mp4.width / 2), int(img_mp4.height / 2)))
img_mp3 = Image.open(os.path.join(EXE_LOCATION, "button_mp3.png"))
img_mp3 = img_mp3.resize((int(img_mp3.width / 2), int(img_mp3.height / 2)))
img_download = Image.open(os.path.join(EXE_LOCATION, "button_download.png"))
img_download = img_download.resize((int(img_download.width / 2), int(img_download.height / 2)))

import pygame
pygame.mixer.init()

root = Tk()
root.geometry("500x400")
root.title("KinitoPET likes piracy")
root.resizable(0, 0)
root.iconbitmap(airy2)

bg_color = "#fee7ff"
root.configure(background=bg_color)

airy1 = ImageTk.PhotoImage(airy1)
img_mp4 = ImageTk.PhotoImage(img_mp4)
img_mp3 = ImageTk.PhotoImage(img_mp3)
img_download = ImageTk.PhotoImage(img_download)

link = StringVar()

# Add padding and center align elements
Label(root, text="Hi, I'm KinitoPET, and I like piracy", bg=bg_color, font=("Helvetica", 16)).pack(pady=10)
Label(root, image=airy1, bg=bg_color).pack(pady=10)
Label(root, text="Paste any YouTube link so I can download it for you:", bg=bg_color, font=("Helvetica", 12)).pack(pady=10)
Entry(root, width=70, textvariable=link).pack(pady=10)

pygame.mixer.music.load(os.path.join(EXE_LOCATION,'kinito_OST.mp3')); pygame.mixer.music.play(loops=-1)
pygame.mixer.Sound(os.path.join(EXE_LOCATION,'hi.mp3')).play()

mp = StringVar()
mp4 = Button(root, text="MP4", command=lambda: extension_select("mp4"), image=img_mp4, bg=bg_color, bd=0)
mp4.place(relx=0.3, rely=0.6, anchor=CENTER)
mp3 = Button(root, text="MP3", command=lambda: extension_select("mp3"), image=img_mp3, bg=bg_color, bd=0)
mp3.place(relx=0.7, rely=0.6, anchor=CENTER)

def extension_select(ex):
    global mp
    mp = ex
    if mp == "mp4":
        mp4["state"] = "disabled"
        mp3["state"] = "normal"
    if mp == "mp3":
        mp4["state"] = "normal"
        mp3["state"] = "disabled"

extension_select("mp4")

from pytubefix import YouTube
def Downloader():
    def delete(): dwnl.destroy(); btn["state"] = "normal"
    btn["state"] = "disabled"
    try:
        if mp == "mp4": url = YouTube(str(link.get())); video = url.streams.get_highest_resolution(); video.download(downloads)
        else: url = YouTube(str(link.get())); audio = url.streams.get_audio_only(); audio.download(downloads, mp3=True)
    except Exception as e: dwnl = Label(root, text="I couldn't download your video :( \n" + str(e)); dwnl.place(relx=0.5, rely=0.5, anchor=CENTER); pygame.mixer.Sound(os.path.join(EXE_LOCATION,'error.mp3')).play(); dwnl.after(3000, delete);return
    else: dwnl = Label(root, text="Downloaded :DD (check your downloads folder)"); dwnl.place(relx=0.5, rely=0.5, anchor=CENTER); pygame.mixer.Sound(os.path.join(EXE_LOCATION,'download.mp3')).play(); dwnl.after(5000, delete)

btn = Button(root, text="Download", command=Downloader, bg=bg_color, image=img_download, bd=0)
btn.pack(pady=20)

root.mainloop()