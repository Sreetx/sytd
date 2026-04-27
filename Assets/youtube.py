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

# Import modul dasar
import time, os, sys, tempfile
from pytubefix import YouTube
from rich.console import Console
from rich import print as rprint
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED

from PIL import Image
from io import BytesIO
from term_image.image import AutoImage
import requests

import ffmpeg
from pathlib import Path
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import prompt
from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeRemainingColumn
import subprocess

# Path default untuk download

paths = Path.home() / "Downloads"

# Inisiasi dulu ya guys
console = Console()

# Buka file link tadi
tmp_dir = tempfile.gettempdir()
path_jembatan = os.path.join(tmp_dir, "link.link")
with open (path_jembatan, 'r', encoding='UTF-8') as f:
    url = f.read().strip()

# Inisiasi pytubefix
try:
    yt = YouTube(url)

except Exception as e:
    rprint ('\n[bold red] ! [/bold red]Something went wrong')
    rprint ('[bold orange1] * [/bold orange1]Please check your link or Internet Connection')
    exit()

# Cari dan kita print thumbnail nya
def thumbnail_print(thumbnail):
    req = requests.get(thumbnail, timeout=5)
    img_data = BytesIO(req.content)
    img = Image.open(img_data)
    images =  AutoImage(img, width=40)

    print(images)

# Show all resolution
def show_all_res(res):
    rprint ("\n[bold green] * [/bold green]List of available video resolution")
    table = Table(show_header=True, box=ROUNDED, border_style='green')
    table.add_column('No.', justify='center')
    table.add_column('Resolution', justify='center')
    table.add_column('Status', justify='center')
    table.add_column('Codec', justify='center')
    table.add_column('Size', justify='center')

    download_mapping = {}
    for index, s in enumerate(res, start=1):
        download_mapping[str(index)] = s
        ext = s.mime_type.split('/')[-1].upper()
        v_codec = s.video_codec if s.includes_video_track else ""
        codec_name = "H.264" if "avc1" in v_codec else "H.265" if "hev" in v_codec else "Unknown"
        aud_ext = ext if codec_name != "Unknown" else s.audio_codec.split('/')[-1].upper() if s.audio_codec else "Unknown"

        # Logika Status di Tabel (Kita samarkan biar user tau ini bakal dapet audio)
        if s.includes_video_track:
            status = f"[#62d8eb]Video + Audio[/#62d8eb] [dim]({ext})[/dim]"
            quality = s.resolution
        else:
            status = f"[#8ad0f0]Audio Only[/#8ad0f0] [dim]({aud_ext})[/dim]"
            quality = "Music"
        
        # Tambah estimasi size kalo dia perlu di-merge (video dash + audio)
        display_size = s.filesize
        if s.includes_video_track and not s.includes_audio_track:
            display_size += 5 * 1024 * 1024 # Estimasi audio
            
        table.add_row(str(index), quality or 'N/A', status, codec_name, f'{display_size / (1024*1024):.2f} MB')

    console.print(table)
    return download_mapping


# progress bar nya ya
def download_with_progress(stream, paths, prefix=""):
    total_size = stream.filesize
    with Progress(
        TextColumn("[bold blue]{task.description}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•", TransferSpeedColumn(), "•", TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task(f"[#62d8eb]Downloading...[/#62d8eb]", total=total_size)
        def update_bar(stream, chunk, bytes_remaining):
            progress.update(task, completed=total_size - bytes_remaining)
        
        yt.register_on_progress_callback(update_bar)
        return stream.download(output_path=paths, filename_prefix=prefix)


# Logika downloadnya
def download_logic(mapping):
    choice = prompt(HTML('\n<orange>? </orange>Select a number to download: '))
    if choice not in mapping:
        rprint("[bold red]![/bold red] Wrong Number!"); return
        
    stream = mapping[choice]    
    # Kalo pilihannya Video Mute (High Res) -> Auto Merge FFmpeg
    if stream.includes_video_track and not stream.includes_audio_track:
        rprint("\n[yellow]*[/yellow] High resolution is selected. Downloading Video & Audio...")
        v_file = download_with_progress(stream, paths, "v_")
        
        a_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        a_file = download_with_progress(a_stream, paths, "a_")

        if v_file is None or a_file is None:
            pass # Error handling sudah ada di download_with_progress, jadi kita  skip aja
        
        final_name = f"{yt.title}".replace("/", "-").replace('"', '')
        final_path = os.path.join(paths, final_name)
        
        rprint(f"[green]~[/green] Merging with FFmpeg...")
        try:
            (
                ffmpeg
                .output(
                    ffmpeg.input(v_file), 
                    ffmpeg.input(a_file), 
                    str(final_path), 
                    vcodec='copy', 
                    acodec='copy'
            )
            .run(quiet=True, overwrite_output=True)
            )
        except ffmpeg.Error as e:
            rprint(f"[bold red]![/bold red] Error occurred while merging: {e}")

        os.remove(v_file); os.remove(a_file)
        rprint(f"\n[bold reverse green] SUCCESS [/bold reverse green] {stream.default_filename}")
        rprint(f"[bold green]✓[/bold green] Saved to: [orange1]{paths}/{stream.default_filename}[/orange1]")
        os.system(f'notify-send "Download Done" "{yt.title}" -i video-display')
    else:
        # Kalo pilihannya Audio Only atau Video 360p (sudah ada audio)
        download_with_progress(stream, paths)
        rprint(f"\n[bold reverse green] SUCCESS [/bold reverse green] {stream.default_filename}")
        rprint(f"[bold green]✓[/bold green] Saved to: [orange1]{paths}/{stream.default_filename}[/orange1]")
        os.system(f'notify-send "Download Done" "{yt.title}" -i video-display')

# Filter stream untuk dapetin yang terbaik (Video Mute H.264, Video+Audio Progressive, Audio Only)
def filter_best_streams():
    # Ambil Video Mute (High Res) - Ambil 2 teratas
    v_mute = yt.streams.filter(
        only_video=True, 
        file_extension='mp4',
        custom_filter_functions=[lambda s: s.video_codec and s.video_codec.startswith('avc1')]
    ).order_by('resolution').desc()[:2]

    # Ambil Video + Audio (Progressive) yang biasanya emang H.264
    v_full = yt.streams.filter(
        progressive=True, 
        file_extension='mp4'
    ).order_by('resolution').desc()[:1]

    # Audio tetep ambil yang terbaik (m4a/aac paling aman)
    a_only = yt.streams.filter(
        only_audio=True, 
        file_extension='mp4',
        custom_filter_functions=[lambda s: s.audio_codec and s.audio_codec.startswith('mp4a')]
    ).order_by('abr').desc()[:2]

    return list(v_mute) + list(v_full) + list(a_only)


def description(descript):
    console.print(Panel(descript, expand=False, border_style='orange1', title="[bold green]Description[/bold green]"))

# Ambil semua metadata nya
def get_all_data():
    title = yt.title
    author = yt.author
    views = f'{yt.views:,}'
    length = f'{yt.length // 60}:{yt.length % 60:02d}'
    rating = f"{yt.rating}" if yt.rating else 'N/A'
    descript = yt.description
    thumbnail = yt.thumbnail_url
    res = filter_best_streams()

    head = Text.from_markup("[bold green]YouTube Video Downloader![/bold green]")

    print('')

    console.print(Panel(head, expand=False, border_style='orange1'))

    thumbnail_print(thumbnail)

    info = Table(show_header=False, show_edge=False, pad_edge=False, box=None)
    info.add_row("[bold green]>[/bold green]", "[orange1]Title[/orange1]", f': {title}')
    info.add_row("[bold green]>[/bold green]", "[orange1]Channel[/orange1]", f': {author}')
    info.add_row("[bold green]>[/bold green]", "[orange1]Total Views[/orange1]", f': {views}')
    info.add_row("[bold green]>[/bold green]", "[orange1]Rating[/orange1]", f': {rating}')
    info.add_row("[bold green]>[/bold green]", "[orange1]Length[/orange1]", f': {length}')

    console.print(info)

    #Show description
    t1 = prompt(HTML("\n<orange>? </orange>Show description? (y/n): "))
    if t1 == 'y' or t1 == 'Y':
        description(descript)

    # Download or show another resolution
    rprint('\n[bold orange1]? [/bold orange1]Download with High Quality or see another options?')
    rprint('[green]D[/green] = Download (Video + Audio High Definition)\n[yellow]L[/yellow] = Show all options')
    download = prompt(HTML('<green> > </green>: '))
    if download == 'd' or download == 'D':
        # 1. Cari Video 1080p/Terbaik (Khusus H.264/avc1)
        v_stream = yt.streams.filter(
            only_video=True, 
            file_extension='mp4',
            custom_filter_functions=[lambda s: s.video_codec and s.video_codec.startswith('avc1')]
        ).order_by('resolution').desc().first()

        # 2. Cari Audio Terbaik (AAC/mp4a)
        a_stream = yt.streams.filter(
            only_audio=True, 
            file_extension='mp4',
            custom_filter_functions=[lambda s: s.audio_codec and s.audio_codec.startswith('mp4a')]
        ).order_by('abr').desc().first()

        if v_stream and a_stream:
            # Banner Styling
            banner_d = Panel(
                Text.from_markup(f"[bold white]ULTRA QUICK DOWNLOAD (1080p+)[/bold white]\n[dim]Codec: H.264 + AAC | Mode: Auto-Merge[/dim]"),
                border_style="bold orange1", expand=False, padding=(0, 2)
            )
            console.print(banner_d)
            
            # Eksekusi Double Download
            rprint(f"[bold green]>[/bold green] Fetching Video ({v_stream.resolution})...")
            v_file = download_with_progress(v_stream, paths, "TEMP_V_")
            
            rprint(f"[bold green]>[/bold green] Fetching Audio ({a_stream.abr})...")
            a_file = download_with_progress(a_stream, paths, "TEMP_A_")

            # Final Output Name
            final_name = f"{yt.title}.mp4".replace("/", "-").replace('"', '')
            final_path = os.path.join(paths, final_name)

            # Proses Kawin Pakai FFmpeg
            rprint(f"[bold green]~[/bold green] Merging into final file...")
            rprint(f"[green]~[/green] Merging with FFmpeg...")
            try:
                (
                    ffmpeg
                    .output(
                        ffmpeg.input(v_file), 
                        ffmpeg.input(a_file), 
                        str(final_path), 
                        vcodec='copy', 
                        acodec='copy'
                )
                .run(quiet=True, overwrite_output=True)
                )
            except ffmpeg.Error as e:
                rprint(f"[bold red]![/bold red] Error occurred while merging: {e}")

            os.remove(v_file); os.remove(a_file)
            rprint(f"\n[bold reverse green] SUCCESS [/bold reverse green] {final_name}")
            rprint(f"[bold green]✓[/bold green] Saved to: [orange1]{paths}/{final_name}[/orange1]")
            os.system(f'notify-send "Download Done" "{yt.title}" -i video-display')
            exit()

        else:
            rprint("[bold red]![/bold red] Failed to find the right stream.")
    else:
        # Jika pilih L, tampilin tabel dan jalankan logika input nomor
        mapping = show_all_res(res) # Ambil mapping-nya
        download_logic(mapping)
        os.system(f'notify-send "Download Done" "{yt.title}" -i video-display')

try:
    get_all_data()
except KeyboardInterrupt:
    rprint("\n[bold red]![/bold red] Download cancelled by user.")
    exit()