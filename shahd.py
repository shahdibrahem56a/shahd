from tkinter import *
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import signal

# Global control flags
cancel_flag = False
pause_flag = False

# Functions
def download_with_ytdlp(url, save_path, options):
    global cancel_flag, pause_flag
    try:
        command = ['yt-dlp', '-o', f'{save_path}/%(title)s.%(ext)s'] + options + [url]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in process.stdout:
            if cancel_flag:
                process.terminate()
                progress_var.set(0)
                speed_label.config(text="Download cancelled.")
                messagebox.showinfo("Cancelled", "Download was cancelled.")
                cancel_flag = False
                return

            if pause_flag:
                speed_label.config(text="Paused.")
                while pause_flag and not cancel_flag:
                    threading.Event().wait(0.1)  # Sleep briefly to avoid busy-waiting

            # Extract progress and speed
            if "MiB/s" in line:
                parts = line.strip().split()
                try:
                    speed = [part for part in parts if "MiB/s" in part][0]
                    progress_var.set(float(parts[1].strip('%')))
                    speed_label.config(text=f"Speed: {speed}")
                except (IndexError, ValueError):
                    pass

        process.wait()
        if process.returncode == 0:
            messagebox.showinfo("Success", "Download completed successfully!")
        else:
            raise Exception(process.stderr.read().strip())
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def start_download(options):
    global cancel_flag, pause_flag
    cancel_flag = False
    pause_flag = False
    toggle_pause_button.config(text="Pause")  # Reset button state
    url = myentry.get()
    if not url.startswith("https://www.youtube.com/"):
        messagebox.showerror("Error", "Please enter a valid YouTube URL")
        return
    save_path = filedialog.askdirectory(title="Select Download Folder")
    if not save_path:
        messagebox.showinfo("Cancelled", "Download cancelled")
        return
    progress_var.set(0)
    speed_label.config(text="Starting download...")
    threading.Thread(target=download_with_ytdlp, args=(url, save_path, options), daemon=True).start()

def cancel_download():
    global cancel_flag
    cancel_flag = True

def toggle_pause_continue():
    global pause_flag
    pause_flag = not pause_flag
    if pause_flag:
        toggle_pause_button.config(text="Continue")
    else:
        toggle_pause_button.config(text="Pause")

# GUI
root = Tk()
root.geometry("500x350")
root.title("YouTube Downloader")
root.resizable(False, False)

# Label
mylabel = Label(root, text="Enter the video link", font=("Arial", 12))
mylabel.pack(pady=10)

# Entry field
myentry = ttk.Entry(root, width=50, font=("Arial", 12))
myentry.pack(pady=10)

# Buttons
button1 = ttk.Button(root, text="High quality download", command=lambda: start_download(['-f', 'best']))
button1.place(x=100, y=100)

button2 = ttk.Button(root, text="Low quality download", command=lambda: start_download(['-f', 'worst']))
button2.place(x=250, y=100)

button3 = ttk.Button(root, text="Only audio", command=lambda: start_download(['-f', 'bestaudio', '--extract-audio', '--audio-format', 'mp3']))
button3.place(x=200, y=140)

# Cancel Button
cancel_button = ttk.Button(root, text="Cancel", command=cancel_download)
cancel_button.place(x=250, y=200)

# Toggle Pause/Continue Button
toggle_pause_button = ttk.Button(root, text="Pause", command=toggle_pause_continue)
toggle_pause_button.place(x=150, y=200)

# Progress bar
progress_var = DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=400)
progress_bar.pack(pady=80)

# Speed label
speed_label = Label(root, text="", font=("Arial", 10))
speed_label.pack(pady=30)

# Make the app last forever until you close it
root.mainloop()