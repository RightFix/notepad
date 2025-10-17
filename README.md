# Notepad (Kivy/KivyMD)

A small Notepad-style app built with KivyMD.

Features
- Simple text editor
- Save action (button wired to app.save_file)

Run
1. Create and activate a Python virtual environment (Windows PowerShell):

```powershell
py -3 -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Requirements
- See `requirements.txt` for dependencies.

License
- MIT
