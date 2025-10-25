import yt_dlp
import os
import re
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2
from PIL import Image
import tempfile
import random
import time

def download_youtube_audio(url, download_folder='downloads'):
    """
    YouTube audio letöltése MP3 formátumban - alternatív megközelítéssel
    """
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # EXTRA BOT VÉDELEM MEGKERÜLÉSE
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': os.path.join(download_folder, '%(title).100s.%(ext)s'),
        'restrictfilenames': True,
        'windowsfilenames': True,

        # Bot védelem megkerülésére
        'extract_flat': False,
        'quiet': True,
        'no_warnings': False,
        'ignoreerrors': False,
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'audioquality': '0',

        # HTTP headers bot védelem megkerülésére
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Connection': 'keep-alive',
            'Referer': 'https://www.youtube.com/',
        },
    }

    try:
        print("YouTube letöltés indítása...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Először csak információ gyűjtés
            try:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'unknown')
                thumbnail_url = info.get('thumbnail', '')
                print(f"Video info sikeres: {title}")
            except Exception as e:
                print(f"Info gathering failed: {e}")
                return None, "Nem sikerült elérni a YouTube videót"

            # Random delay
            time.sleep(random.uniform(2, 5))

            # Letöltés
            try:
                ydl.download([url])
                print("Letöltés befejezve")
            except Exception as e:
                print(f"Download error: {e}")
                return None, f"Letöltési hiba: {str(e)}"

            # Fájl keresése
            downloaded_file = None
            max_wait = 10  # másodperc
            waited = 0

            while waited < max_wait:
                for file in os.listdir(download_folder):
                    if file.endswith('.mp3'):
                        downloaded_file = file
                        break

                if downloaded_file:
                    break

                time.sleep(1)
                waited += 1
                print(f"Fájl keresése... {waited}s")

            if downloaded_file:
                file_path = os.path.join(download_folder, downloaded_file)
                print(f"Fájl megtalálva: {downloaded_file}")

                # Thumbnail hozzáadása
                if thumbnail_url:
                    try:
                        success = add_cover_art_manually(file_path, thumbnail_url, title)
                        if success:
                            print("Cover art sikeresen hozzáadva")
                        else:
                            print("Cover art hozzáadása sikertelen")
                    except Exception as e:
                        print(f"Cover art hiba: {e}")

                return file_path, title
            else:
                return None, "A letöltött fájl nem található a mappában"

    except Exception as e:
        error_msg = f"Hiba a letöltés során: {str(e)}"
        print(f"Végső hiba: {error_msg}")
        return None, error_msg

def add_cover_art_manually(file_path, thumbnail_url, title):
    """Cover art hozzáadása az MP3-hoz"""
    try:
        # Thumbnail letöltése
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.youtube.com/'
        }

        response = requests.get(thumbnail_url, headers=headers, timeout=30)
        if response.status_code != 200:
            return False

        # Ideiglenes fájl
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name

        # Optimalizálás
        optimized_thumb = optimize_thumbnail(temp_path)

        # MP3 tag-ek
        try:
            audio = MP3(file_path, ID3=ID3)
        except:
            audio = MP3(file_path)

        if audio.tags is None:
            audio.add_tags()

        # Cover art hozzáadása
        with open(optimized_thumb, 'rb') as thumb_file:
            audio.tags.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=thumb_file.read()
                )
            )

        # Cím hozzáadása
        audio.tags.add(TIT2(encoding=3, text=title))

        # Mentés
        audio.save()

        # Takarítás
        try:
            os.unlink(temp_path)
            if optimized_thumb != temp_path:
                os.unlink(optimized_thumb)
        except:
            pass

        return True

    except Exception as e:
        print(f"Cover art hiba: {e}")
        return False

def optimize_thumbnail(thumbnail_path, max_size=(500, 500)):
    """Thumbnail optimalizálása"""
    try:
        with Image.open(thumbnail_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            optimized_path = thumbnail_path.replace('.jpg', '_optimized.jpg')
            img.save(optimized_path, 'JPEG', quality=85, optimize=True)
            return optimized_path
    except Exception as e:
        print(f"Thumbnail optimalizálás hiba: {e}")
        return thumbnail_path

# Alternatív megoldás - egyszerűbb verzió
def download_youtube_simple(url, download_folder='downloads'):
    """Egyszerű YouTube letöltés - kevesebb beállítással"""
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'unknown')

            # Fájl keresése
            for file in os.listdir(download_folder):
                if file.endswith('.mp3') and title in file:
                    return os.path.join(download_folder, file), title

            return None, "Fájl nem található"

    except Exception as e:
        return None, f"Hiba: {str(e)}"