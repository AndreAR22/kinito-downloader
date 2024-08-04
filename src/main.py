from tkinter import *
from PIL import ImageTk, Image
import os
import winreg

reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
downloads = winreg.QueryValueEx(reg_key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
winreg.CloseKey(reg_key)

EXE_LOCATION = os.path.dirname(os.path.realpath(__file__ ))
airy1 = Image.open(os.path.join(EXE_LOCATION, "airy1.png"))
airy2 = os.path.join(EXE_LOCATION, "airy2.ico")
airy1 = airy1.resize((int(airy1.width/4), int(airy1.height/4)))

root = Tk()
root.geometry("500x300")
root.title("Airy likes piracy")
root.resizable(0,0)
root.iconbitmap(airy2)

airy1 = ImageTk.PhotoImage(airy1)
link = StringVar()

Label(root, text="Hi, I'm Airy, and I like piracy").pack()
Label(root, image=airy1).pack()
Label(root, text="\nPaste any YouTube link so I can download it for you:").pack()
Entry(root, width=70, textvariable=link).pack()

mp = StringVar()
mp4 = Button(root, text="MP4", command=lambda:extension_select("mp4"))
mp4.place(x=90, y = 60)
mp3 = Button(root, text="MP3", command=lambda:extension_select("mp3"))
mp3.place(x=90, y = 90)

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
from moviepy.editor import *
import subprocess
def Downloader():
    def delete(): dwnl.destroy(); btn["state"] = "normal"
    btn["state"] = "disabled"
    try:
        if mp == "mp4": url = YouTube(str(link.get())); video = url.streams.get_highest_resolution(); video.download(downloads)
        else: url = YouTube(str(link.get())); audio = url.streams.filter(only_audio=True).first().download(downloads, filename_prefix="AUDIO_"); print(audio); #audio_convert(audio)
        #else: url = YouTube(str(link.get())); audio = url.streams.filter(only_audio=True).first().download(downloads); name, ext = os.path.splitext(audio); mp3_file = name + '.mp3'; os.rename(audio, mp3_file)
    except Exception as e: dwnl = Label(root, text="I couldn't download your video :( \n" + str(e)); dwnl.pack(); dwnl.after(3000, delete); return
    else: dwnl = Label(root, text="Downloaded :DD (check your downloads folder)"); dwnl.pack(); dwnl.after(5000, delete)

    def audio_convert(file):
        video = VideoFileClip(file) 
        video.audio.write_audiofile("example.mp3")

btn = Button(root, text="Download", command=Downloader)
btn.pack()

root.mainloop()