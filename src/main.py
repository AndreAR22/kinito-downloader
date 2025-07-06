from tkinter import *
from tkinter import ttk, filedialog
from PIL import ImageTk, Image
import os
import winreg
import subprocess
import threading
import pygame
import json
import pathlib

APP_NAME = "KinitoDownloader"
SETTINGS_FILE_NAME = "settings.txt"

def get_app_data_path():
    app_data = os.getenv('APPDATA')
    if app_data:
        app_data_path = pathlib.Path(app_data) / APP_NAME
        app_data_path.mkdir(parents=True, exist_ok=True)
        return app_data_path
    return pathlib.Path.cwd() / APP_NAME

APP_DATA_DIR = get_app_data_path()
SETTINGS_FILE_PATH = APP_DATA_DIR / SETTINGS_FILE_NAME

default_downloads_path = ""
try:
    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
    default_downloads_path = winreg.QueryValueEx(reg_key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
    winreg.CloseKey(reg_key)
except Exception:
    default_downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

current_settings = {
    "download_directory": default_downloads_path,
    "music_muted": False
}

all_controllable_sounds = []

def update_all_sound_volumes():
    volume = 0 if current_settings["music_muted"] else 1
    pygame.mixer.music.set_volume(volume)
    for sound_obj in all_controllable_sounds:
        sound_obj.set_volume(volume)

def load_settings():
    global current_settings, downloads
    if SETTINGS_FILE_PATH.exists():
        try:
            with open(SETTINGS_FILE_PATH, 'r') as f:
                loaded_settings = json.load(f)
                current_settings.update(loaded_settings)
        except json.JSONDecodeError:
            pass
    
    downloads = current_settings["download_directory"]
    update_all_sound_volumes()

def save_settings():
    with open(SETTINGS_FILE_PATH, 'w') as f:
        json.dump(current_settings, f, indent=4)

EXE_LOCATION = os.path.dirname(os.path.realpath(__file__))
kinito1 = Image.open(os.path.join(EXE_LOCATION, "kinito1.png"))
kinito2 = os.path.join(EXE_LOCATION, "kinito2.ico")
kinito1 = kinito1.resize((int(kinito1.width / 3), int(kinito1.height / 3)))

img_mp4 = Image.open(os.path.join(EXE_LOCATION, "button_mp4.png"))
img_mp4 = img_mp4.resize((int(img_mp4.width / 2), int(img_mp4.height / 2)))
img_mp3 = Image.open(os.path.join(EXE_LOCATION, "button_mp3.png"))
img_mp3 = img_mp3.resize((int(img_mp3.width / 2), int(img_mp3.height / 2)))
img_download = Image.open(os.path.join(EXE_LOCATION, "button_download.png"))
img_download = img_download.resize((int(img_download.width / 2), int(img_download.height / 2)))

pygame.mixer.init()

root = Tk()
root.title("KinitoPET likes piracy")
root.resizable(0, 0)
root.iconbitmap(kinito2)

window_width = 500
window_height = 400

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)

root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

bg_color = "#fee7ff"
root.configure(background=bg_color)

kinito1 = ImageTk.PhotoImage(kinito1)
img_mp4 = ImageTk.PhotoImage(img_mp4)
img_mp3 = ImageTk.PhotoImage(img_mp3)
img_download = ImageTk.PhotoImage(img_download)

link = StringVar()

Label(root, text="Hi, I'm KinitoPET, and I like piracy", bg=bg_color, font=("Helvetica", 16)).pack(pady=10)
Label(root, image=kinito1, bg=bg_color).pack(pady=10)
Label(root, text="Paste the link from your social media of choice so I can download the videos or audios for you, at the best quality :)", bg=bg_color, font=("Helvetica", 12), wraplength=410).pack(pady=20)
Entry(root, width=70, textvariable=link).pack(pady=0)

pygame.mixer.music.load(os.path.join(EXE_LOCATION,'kinito_OST.mp3'))
pygame.mixer.music.play(loops=-1)

hi_sound = pygame.mixer.Sound(os.path.join(EXE_LOCATION,'hi.mp3'))
download_start_sound = pygame.mixer.Sound(os.path.join(EXE_LOCATION, 'download-01.mp3'))
download_loop_sound = pygame.mixer.Sound(os.path.join(EXE_LOCATION, 'download-02.mp3'))
download_end_sound = pygame.mixer.Sound(os.path.join(EXE_LOCATION, 'download-03.mp3'))
do_not_close_sound = pygame.mixer.Sound(os.path.join(EXE_LOCATION, 'angry_kinito.mp3'))
settings_music_sound = pygame.mixer.Sound(os.path.join(EXE_LOCATION, 'settings.mp3'))
download_success_sound = pygame.mixer.Sound(os.path.join(EXE_LOCATION, 'download.mp3'))
download_error_sound = pygame.mixer.Sound(os.path.join(EXE_LOCATION, 'error.mp3'))

all_controllable_sounds.extend([
    hi_sound,
    download_start_sound,
    download_loop_sound,
    download_end_sound,
    do_not_close_sound,
    settings_music_sound,
    download_success_sound,
    download_error_sound
])

hi_sound.play()

download_loop_channel = None
settings_music_channel = None

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

yt_dlp_path = os.path.join(EXE_LOCATION, "yt-dlp.exe")

download_window = None
progressbar_ref = None
status_label_ref = None
dwnl_label_ref = None

settings_window = None
settings_current_dir_var = None
settings_mute_var = None

def open_settings_window():
    global settings_window, settings_current_dir_var, settings_mute_var, settings_music_channel

    if settings_window and settings_window.winfo_exists():
        settings_window.lift()
        return

    settings_window = Toplevel(root)
    settings_window.title("KinitoPET Downloader Settings")
    settings_window.resizable(0, 0)
    settings_window.configure(background=bg_color)
    settings_window.iconbitmap(kinito2)
    settings_window.protocol("WM_DELETE_WINDOW", lambda: do_not_close_sound.play())

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    settings_win_width = 450
    settings_win_height = 250

    new_x = root_x + (root_width // 2) - (settings_win_width // 2)
    new_y = root_y + (root_height // 2) - (settings_win_height // 2)
    
    root.withdraw()

    settings_window.geometry(f"{settings_win_width}x{settings_win_height}+{new_x}+{new_y}")

    pygame.mixer.music.pause()
    settings_music_channel = settings_music_sound.play(loops=-1)

    settings_current_dir_var = StringVar(value=current_settings["download_directory"])
    settings_mute_var = BooleanVar(value=current_settings["music_muted"])

    Label(settings_window, text="Download Directory:", bg=bg_color, font=("Helvetica", 10)).pack(pady=(15, 0))
    dir_frame = Frame(settings_window, bg=bg_color)
    dir_frame.pack(pady=5)
    Entry(dir_frame, textvariable=settings_current_dir_var, width=40, state="readonly").pack(side=LEFT, padx=5)
    Button(dir_frame, text="Browse", command=browse_directory, bg="#ffcce0", bd=0, relief="raised", padx=5, pady=2).pack(side=LEFT, padx=5)

    Checkbutton(settings_window, text="Mute All Sounds", variable=settings_mute_var, bg=bg_color, font=("Helvetica", 10), command=update_all_sound_volumes).pack(pady=10)

    button_frame = Frame(settings_window, bg=bg_color)
    button_frame.pack(pady=20)
    Button(button_frame, text="Save", command=apply_settings, bg="#cce0ff", bd=0, relief="raised", padx=15, pady=5).pack(side=LEFT, padx=10)
    Button(button_frame, text="Cancel", command=cancel_settings, bg="#ffcce0", bd=0, relief="raised", padx=15, pady=5).pack(side=LEFT, padx=10)

def browse_directory():
    new_dir = filedialog.askdirectory(initialdir=settings_current_dir_var.get())
    if new_dir:
        settings_current_dir_var.set(new_dir)

def apply_settings():
    global downloads
    current_settings["download_directory"] = settings_current_dir_var.get()
    current_settings["music_muted"] = settings_mute_var.get()
    downloads = current_settings["download_directory"]
    save_settings()
    close_settings_window_and_resume_music()

def cancel_settings():
    close_settings_window_and_resume_music()

def close_settings_window_and_resume_music():
    global settings_window, settings_music_channel
    if settings_window and settings_window.winfo_exists():
        settings_window.destroy()
    settings_window = None

    if settings_music_channel and settings_music_channel.get_busy():
        settings_music_channel.stop()

    pygame.mixer.music.unpause()
    update_all_sound_volumes()
    root.deiconify()

def start_download():
    global download_window, progressbar_ref, status_label_ref, dwnl_label_ref, download_loop_channel
    
    download_window = Toplevel(root)
    download_window.title("KinitoPET is downloading...")
    download_window.resizable(0, 0)
    download_window.configure(background=bg_color)
    download_window.iconbitmap(kinito2)
    download_window.protocol("WM_DELETE_WINDOW", lambda: do_not_close_sound.play())

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    download_win_width = 400
    download_win_height = 150

    new_x = root_x + (root_width // 2) - (download_win_width // 2)
    new_y = root_y + (root_height // 2) - (download_win_height // 2)
    root.withdraw()

    download_window.geometry(f"{download_win_width}x{download_win_height}+{new_x}+{new_y}")

    progressbar_ref = ttk.Progressbar(download_window, orient="horizontal", length=300, mode="determinate")
    progressbar_ref.pack(pady=15)
    progressbar_ref["value"] = 0

    status_label_ref = Label(download_window, text="Initializing...", bg=bg_color, font=("Helvetica", 10))
    status_label_ref.pack(pady=5)

    dwnl_label_ref = Label(download_window, text="", bg=bg_color)
    dwnl_label_ref.pack(pady=5)

    btn["state"] = "disabled"
    mp4["state"] = "disabled"
    mp3["state"] = "disabled"
    
    pygame.mixer.music.pause()
    
    start_channel = download_start_sound.play()
    start_sound_duration_ms = int(download_start_sound.get_length() * 1000) + 50

    def play_loop_conditionally(thread_obj):
        global download_loop_channel
        if thread_obj.is_alive():
            download_loop_channel = download_loop_sound.play(loops=-1)

    download_thread = threading.Thread(target=Downloader)
    root.after(start_sound_duration_ms, lambda: play_loop_conditionally(download_thread)) 
    
    download_thread.start()

def Downloader():
    video_url = str(link.get())

    def update_progress(percentage):
        if progressbar_ref and progressbar_ref.winfo_exists():
            progressbar_ref["value"] = percentage
            status_label_ref.config(text=f"Downloading: {percentage:.1f}%")
            download_window.update_idletasks()

    def update_status_label(message, color="black"):
        if status_label_ref and status_label_ref.winfo_exists():
            status_label_ref.config(text=message, fg=color)
            download_window.update_idletasks()

    def display_final_message(message, color="black", duration=5000):
        if dwnl_label_ref and dwnl_label_ref.winfo_exists():
            dwnl_label_ref.config(text=message, fg=color)
            download_window.update_idletasks()
            download_window.after(duration, close_download_window_and_resume_music)

    try:
        command = [yt_dlp_path]
        if mp == "mp4":
            command.extend([
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
                "-o", f"{downloads}/%(title)s.%(ext)s",
                '--no-mtime',
                video_url
            ])
        else:
            command.extend([
                "-x",
                "--audio-format", "mp3",
                "-o", f"{downloads}/%(title)s.%(ext)s",
                '--no-mtime',
                video_url
            ])

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        for line in process.stdout:
            root.after(0, lambda l=line: update_status_label(l.strip()))
            if "[download]" in line and "%" in line:
                try:
                    percentage_str = line.split("%")[0].split()[-1]
                    percentage = float(percentage_str)
                    root.after(0, lambda p=percentage: update_progress(p))
                except ValueError:
                    pass

        process.wait()
        
        if process.returncode == 0:
            download_success_sound.play(); root.after(0, lambda: display_final_message("Downloaded :DD (check your downloads folder)", color="green"))
        else:
            error_message = f"I couldn't download it, sorry :( \nError Code: {process.returncode}"
            download_error_sound.play(); root.after(0, lambda: display_final_message(error_message, color="red"))

    except Exception as e:
        download_error_sound.play(); root.after(0, lambda: display_final_message(f"An unexpected error occurred: {e}", color="red"))
    finally:
        if download_loop_channel and download_loop_channel.get_busy():
            download_loop_channel.stop()
        download_end_sound.play()

        root.after(0, lambda: (btn.config(state="normal"), extension_select(mp)))

def close_download_window_and_resume_music():
    global download_window
    if download_window and download_window.winfo_exists():
        download_window.destroy()
    download_window = None
    root.deiconify()
    pygame.mixer.music.unpause()
    update_all_sound_volumes()

load_settings()
print(f"Settings file path: {SETTINGS_FILE_PATH}")

btn = Button(root, text="Download", command=start_download, bg=bg_color, image=img_download, bd=0)
btn.pack(pady=10)

settings_button = Button(root, text="⚙️", font=("Arial", 16), command=open_settings_window, bg=bg_color, bd=0, relief="flat", highlightthickness=0)
settings_button.place(relx=0.02, rely=0.02, anchor=NW)

root.mainloop()