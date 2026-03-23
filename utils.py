import sys
import os
import json
import subprocess
import traceback
import platform
from datetime import datetime

def get_work_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

WORK_DIR = get_work_dir()
CACHE_FILE = os.path.join(WORK_DIR, "font_cache.json")
LOG_FILE = os.path.join(WORK_DIR, "error_log.txt")

def log_error(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{now}] {msg}\n")
    except Exception:
        pass

def check_and_setup_dependencies():
    if getattr(sys, 'frozen', False):
        return

    required = ['PIL', 'matplotlib', 'customtkinter', 'pyperclip']
    missing = []
    
    for req in required:
        try:
            __import__(req)
        except ImportError:
            pkg_name = 'Pillow' if req == 'PIL' else req
            missing.append(pkg_name)

    if missing:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        msg = f"必要なライブラリが足りないみたい。\n自動でインストールする？\n不足: {', '.join(missing)}"
        ans = messagebox.askyesno("セットアップ", msg)
        
        if ans:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", *missing], check=True)
                messagebox.showinfo("成功", "インストール完了したよ。アプリを立ち上げるね。")
            except subprocess.CalledProcessError as e:
                err_msg = f"インストール失敗しちゃった。\nコマンドプロンプトで以下を実行してね:\npip install {' '.join(missing)}\n\nPython自体がおかしい場合は:\nwinget install Python.Python.3.12"
                log_error(f"Install Failed: {e}")
                messagebox.showerror("エラー", err_msg)
                sys.exit(1)
        else:
            sys.exit(0)

def force_update_font_cache():
    try:
        from PIL import ImageFont
        font_dirs = []
        current_os = platform.system()

        # OSごとにフォントが置いてある標準的な場所をリストアップ
        if current_os == "Windows":
            font_dirs = [
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')
            ]
        elif current_os == "Darwin":  # Mac
            font_dirs = [
                "/Library/Fonts",
                "/System/Library/Fonts",
                os.path.expanduser("~/Library/Fonts")
            ]
        elif current_os == "Linux":
            font_dirs = [
                "/usr/share/fonts",
                "/usr/local/share/fonts",
                os.path.expanduser("~/.local/share/fonts")
            ]

        font_dict = {}
        for d in font_dirs:
            if os.path.exists(d):
                # フォルダの中をサブフォルダまで全部探しに行く (os.walk)
                for root, _, files in os.walk(d):
                    for file in files:
                        # ここで .otf もしっかりチェック！
                        if file.lower().endswith(('.ttf', '.ttc', '.otf')):
                            path = os.path.join(root, file)
                            try:
                                font = ImageFont.truetype(path, 10)
                                name_tuple = font.getname()
                                name = f"{name_tuple[0]} {name_tuple[1]}".strip()
                                font_dict[name] = path
                            except Exception:
                                continue
        
        sorted_dict = {k: font_dict[k] for k in sorted(font_dict)}
        
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted_dict, f, ensure_ascii=False, indent=2)
            
        return list(sorted_dict.keys())
    except Exception as e:
        log_error(f"Font scan error: {traceback.format_exc()}")
        return []

def load_font_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return list(data.keys())
        except Exception as e:
            log_error(f"Cache load error: {e}")
    return force_update_font_cache()

def get_font_path(font_name):
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get(font_name, "")
        except:
            pass
    return ""

def copy_to_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
    except Exception as e:
        log_error(f"Clipboard error: {e}")

def preview_in_cmd(ansi_text):
    try:
        temp_txt = os.path.join(WORK_DIR, "temp_aa.txt")
        # BOM付きUTF-8で保存してPowerShellの文字化けを防ぐ
        with open(temp_txt, "w", encoding="utf-8-sig") as f:
            f.write(ansi_text)
        
        current_os = platform.system()
        if current_os == "Windows":
            # Windowsの場合はPowerShellで開く
            subprocess.Popen(
                ["powershell.exe", "-NoExit", "-Command", f"Get-Content -Path '{temp_txt}'"],
                cwd=WORK_DIR,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        elif current_os == "Darwin": # Mac
            # Macの場合はTerminalでcatさせる
            cmd = f"cat '{temp_txt}'; echo; echo 'Press Enter to close...'; read"
            subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "{cmd}"'])
        else: # Linuxなど
            # Linuxは標準的な端末エミュレータでcat (環境に依存するけど一例)
            subprocess.Popen(["x-terminal-emulator", "-e", f"sh -c \"cat '{temp_txt}'; read\""])
            
    except Exception as e:
        log_error(f"CMD preview error: {e}")