# main.py
#
# Copyright 2026 Sreetx
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Impor tools dasar
import os, sys, time, threading, glob, subprocess, shutil, builtins
from pathlib import Path
from argparse import ArgumentParser
stop_event = threading.Event()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#Env
rprint = builtins.print

# Cek Dependensi
try:
    def import_module():
        try:
            global orange
            global putih
            global merah
            global hijau
            global biru
            global borange
            global bputih
            global bhijau
            global bmerah
            global banorange
            global bbiru
            global kelabu
            global borangekelip
            global banhijau
            global banmerah
            global banhijau
            global reset
            from Assets.warna import orange
            from Assets.warna import putih
            from Assets.warna import merah
            from Assets.warna import hijau
            from Assets.warna import biru
            from Assets.warna import banorange
            from Assets.warna import borange
            from Assets.warna import bputih
            from Assets.warna import bhijau
            from Assets.warna import bmerah
            from Assets.warna import bbiru
            from Assets.warna import kelabu
            from Assets.warna import borangekelip
            from Assets.warna import banhijau
            from Assets.warna import banmerah
            from Assets.warna import reset
        except ImportError:
            print(" (*) File Assets/warna.py is Missing")
            print(" (*) Please reinstall this script from my github repository!"); sys.exit()
        
        # Cek Paket
        try:
            global prompt
            global ANSI
            global Console
            global Table
            global Panel
            global Text
            global rprint
            from prompt_toolkit import prompt
            from prompt_toolkit import ANSI
            from rich.prompt import Prompt
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            from rich.text import Text
            from urllib.parse import urlparse
            import ffmpeg

            try:
                import rich
                rprint = rich.print
            except ImportError:
                rprint = builtins.print
            import requests
            import pytubefix
            from PIL import Image
            from io import BytesIO
            from term_image.image import AutoImage

            global banner
            from Assets.warna import banner

        except ImportError:
            stop_event.set()
            print(f"\n\n{borange} ? {reset}Missing dependency!")
            install_pt = input (f"{borange} > {reset}Install it? (y/n): ")
            if install_pt not in ['n', 'N']:
                if sys.platform in ['win', 'win32']:
                    subprocess.run(["python", "-m", "pip", "install", "prompt_toolkit", "pytubefix", "requests", "rich", 'pillow', 'term-image', 'ffmpeg-python'])
                else:
                    try:
                        subprocess.run(["sudo", "pacman", "-Syu"])
                    except subprocess.CalledProcessError:
                        print(f"\n{borange} # {reset}Installing Components (APT)..."); time.sleep(0.3)
                        subprocess.run(['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'upgrade'], shell=True)
                        subprocess.run(['sudo', 'apt', 'install', 'python3-requests', 'python3-prompt_toolkit', 'python3-pytubefix', 'python3-rich', 'python3-term-image', 'python3-pillow', 'python3-ffmpeg-python'], shell=True)
                        print(f"\n{borange} # {reset}If the installation error occurs, you can install it manually")
                        for i, h in enumerate(['Requests', 'Prompt Toolkit', 'Pytubefix', 'Rich', 'Pillow', 'Term-Image', 'FFmpeg'], 1): 
                            print(f"{hijau} {i}.{reset} {h}")

                        print (f"\n{bhijau} # {reset}Components installation successfuly")
                        print (f"{bhijau} # {reset}You can use this tools btw"); time.sleep(0.4)
                        exit()

                    paru = shutil.which("paru")
                    yay = shutil.which("yay")
                    if paru and yay:
                        print (f"\n{bhijau} * {reset}Many AUR helper found!")
                        for i, h in enumerate(['paru', 'yay'], 1): 
                            print(f"{hijau} {i}.{reset} {h}")
                        
                        choice = str(input(f"{borange} ? {reset}Choose one: "))
                        if choice.lower() == "1":
                            helper = paru
                        elif choice.lower() == "2":
                            helper = yay
                        else:
                            print(f"{bmerah} # {reset}Please select one!")
                            exit()
                    elif paru:
                        helper = paru
                    elif yay:
                        helper = yay
                        
                    else:
                        print(f"\n{bmerah} ! {reset}AUR helper not found! please install yay or paru"); sys.exit()

                    helper_list = helper.split('/')[-1]

                    print(f"\n{borange} # {reset}Installing Components ({helper_list})..."); time.sleep(0.3)
                    try:
                        subprocess.run([helper, '-S', 'python-requests', 'python-rich', 'python-prompt_toolkit', 'python-pytubefix', 'python-term-image', 'python-pillow', 'python-ffmpeg-python', '--noconfirm'], check=True)
                    except Exception as e:
                        print(f"{bmerah} ! {reset}Something went wrong!")
                        print(e)
                        exit()

                print(f"\n{borange} * {reset}Checking and downloading additional components (PIP)..."); time.sleep(0.3)
                subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
                subprocess.run(["python", "-m", "pip", "install", "requests", "prompt_toolkit", "pytubefix", "rich", 'pillow', 'term-image', 'ffmpeg-python', 'nodejs-wheel', '--break-system-packages'])
                
            print (f"\n{bhijau} # {reset}Components installation successfuly")
            print (f"{bhijau} # {reset}You can use this tools btw"); time.sleep(0.4)
            exit()

except Exception as e:
    print (f"{bmerah} ! {reset}There is an error"); time.sleep(0.2)
    print (e)
    exit()

def loading_animation(teks):
    i = 0
    while not stop_event.is_set():
        dot = '.' * (i % 5)
        print(f"\r {teks}{dot:<5}", end='', flush=True)
        time.sleep(0.3)
        i += 1

def run_with_animation(func, teks):
    loading_thread = threading.Thread(target=loading_animation, args=(teks,))
    loading_thread.start()
    try:
        func()
    except ImportError:
        stop_event.set()
        sys.exit()
    finally:
        stop_event.set()
        loading_thread.join()
    stop_event.set()
    loading_thread.join()

try:
    run_with_animation(import_module, "[*] Importing Module")
except (KeyboardInterrupt, OSError):
    rprint("\n[bold red]![/bold red] Exiting...")
    exit()

# Biar keren dikit lah kalo di exit
try:
    # Print Banner
    subprocess.run(['clear']) or subprocess.run(['cls'])
    banner()

    # Pake rprint biar mantep. bikin sendiri btw var nya ya.
    rprint (f'\n[orange1] * [/orange1]Please insert the link')
    prompt_ansi = ANSI(f"{orange} > {reset}: ")

    # Biar mudah simpan dulu ke teks link nya
    link = prompt(prompt_ansi)
    ROOT = Path(__file__).parent
    with open (ROOT / "Assets/link.link", 'w') as f:
        f.write(link)

# Biar bisa tanpa https di input
    if not link.startswith(('http://', 'https://')):
        link = 'https://' + link

# Detect Platform
    link = link.lower()
    mapping = {
        'youtube.com' : 'YouTube',
        'youtu.be' : 'YouTube',
        'facebook.com' : 'Facebook',
        'fb.watch' : 'Facebook',
        'instagram.com' : 'Instagram',
        'tiktok.com' : 'TikTok',
        'vm.tiktok.com' : 'TikTok'
        }

    for key, name in mapping.items():
        if key in link:
            platform = name
            break
    else:
        rprint ('\n[bold red] ! [/bold red]Unknown Platform')
        exit()

except (KeyboardInterrupt, OSError):
    rprint("\n[bold red]![/bold red] Exiting...")
    exit()  

if platform == 'YouTube':
    from Assets import youtube

elif platform == 'Facebook':
    rprint (f'\n[bold orange1] # [/bold orange1]The {platform} video download feature is not yet available')
    rprint ('[bold orange1] * [/bold orange1]Wait for the next update!')
    exit()

elif platform == 'Instagram':
    rprint (f'\n[bold orange1] # [/bold orange1]The {platform} video download feature is not yet available')
    rprint ('[bold orange1] * [/bold orange1]Wait for the next update!')
    exit()

elif platform == 'TikTok':
    rprint (f'\n[bold orange1] # [/bold orange1]The {platform} video download feature is not yet available')
    rprint ('[bold orange1] * [/bold orange1]Wait for the next update!')
    exit()

else:
    rprint ('\n[bold red] ! [/bold red]Unknown Platform')
    exit()

