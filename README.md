# BotBuilder Setup Guide

## For New Laptop (Python 3.11 Required)

### Step 1: Install Python 3.11

Even if you have Python 3.12 or newer installed, you need Python 3.11 specifically:

1. Download **Python 3.11.9** from: https://www.python.org/downloads/release/python-3119/
2. Scroll down to "Files" section
3. Download: **Windows installer (64-bit)**
4. Run installer:
   - ✅ Check "Add python.exe to PATH"
   - Click "Customize installation"
   - Click "Next"
   - ✅ Check "Install for all users"
   - Change install location to: `C:\Python311`
   - Click "Install"

### Step 2: Verify Python 3.11 Installation

```powershell
# Check version
C:\Python311\python.exe --version
# Should show: Python 3.11.9
```

### Step 3: Create Project Folder and Venv

```powershell
# Create new folder
mkdir C:\BotBuilder
cd C:\BotBuilder

# Create venv using Python 3.11
C:\Python311\python.exe -m venv venv

# Activate venv
venv\Scripts\activate

# Verify you're using Python 3.11
python --version
# Should show: Python 3.11.9
```

### Step 4: Install Required Packages

```powershell
# Make sure venv is activated (you should see "(venv)" in prompt)
pip install pyinstaller python-telegram-bot==13.15 pillow psutil opencv-python pyaudio
```

### Step 5: Copy BotBuilder Files

Copy **ONLY** these files from your old laptop to `C:\BotBuilder`:

```
C:\BotBuilder\
  ├── BotBuilder.exe           # Copy this
  ├── telebot_lite.py          # Copy this
  └── upx\                     # Copy this folder
```

**DO NOT copy venv** - you already created it in Step 3!

### Step 6: Run BotBuilder

```powershell
cd C:\BotBuilder
.\BotBuilder.exe
```

---

## Folder Structure

Your final setup should look like:

```
C:\BotBuilder\
  ├── BotBuilder.exe           # Main application
  ├── telebot_lite.py          # Bot template
  ├── upx\                     # Compression tool
  │   ├── upx.exe
  │   └── ...
  └── venv\                    # Python 3.11 environment
      ├── Scripts\
      │   ├── python.exe
      │   ├── pip.exe
      │   └── ...
      └── Lib\
```

---

## Building a Bot

1. Run `BotBuilder.exe`
2. Enter:
   - **Bot Name**: MyBot
   - **Bot Token**: (from @BotFather)
   - **Camera Index**: 1
   - ✅ Check "Add to Windows Startup" (optional)
3. Click **Build Bot Executable**
4. Wait 2-3 minutes
5. Find your bot: `build_MyBot\dist\MyBot.exe`

---

## Features

### ✅ Startup Feature
- Bot automatically runs on Windows startup
- Waits for internet connection (up to 5 minutes)
- Auto-registers in Windows Registry

### ✅ Internet Check
- Waits for connection before starting
- Tests Google DNS (8.8.8.8) and Telegram API
- Shows progress messages every 5 seconds

### ✅ Portable
- Created bots are 100% standalone
- No Python needed to run the bot
- Copy to any Windows PC and run

---

## Troubleshooting

### "Python 3.11 not found" Error
- Make sure Python 3.11 is installed at `C:\Python311\python.exe`
- OR create venv in same folder as BotBuilder.exe

### "PyInstaller not found" Error
```powershell
# Activate venv and install
cd C:\BotBuilder
venv\Scripts\activate
pip install pyinstaller
```

### Bot doesn't start after reboot
- Check internet connection
- Bot waits up to 5 minutes for connection
- Check startup in: `Win+R` → `shell:startup`

---

## Multiple Python Versions

If you have Python 3.12+ installed:

```powershell
# Use specific Python 3.11 to create venv
C:\Python311\python.exe -m venv venv

# NOT this (might use wrong version):
python -m venv venv
```

---

## Quick Test

```powershell
# Test the setup
cd C:\BotBuilder
venv\Scripts\activate
python --version  # Should be 3.11.x
python -m pip show pyinstaller  # Should show PyInstaller info
.\BotBuilder.exe  # Should open GUI
```

---

## Notes

- BotBuilder.exe searches for Python 3.11 automatically
- Checks: venv folder, C:\Python311, Program Files, PATH
- Verifies Python version before building
- Only Python 3.11.x is accepted (3.10, 3.12 will be rejected)
