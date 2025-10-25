from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'titkos_kulcs_123'

# Konfiguráció
DOWNLOAD_FOLDER = 'downloads'
DATABASE = 'music_downloader.db'

# Adatbázis inicializálása
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    create_table_sql = """
                       CREATE TABLE IF NOT EXISTS downloads (
                                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                service TEXT NOT NULL,
                                                                title TEXT,
                                                                url TEXT,
                                                                quality TEXT,
                                                                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                       ) \
                       """

    c.execute(create_table_sql)
    conn.commit()
    conn.close()

# Főoldal
@app.route('/')
def index():
    return render_template('index.html')

# Zenéletöltő főoldal
@app.route('/zeneletolto')
def zeneletolto_main():
    return render_template('zeneletolto_main.html')

# YouTube letöltés oldal
@app.route('/zeneletolto/youtube')
def youtube_download():
    return render_template('youtube_download.html')

# Spotify letöltés oldal
@app.route('/zeneletolto/spotify')
def spotify_download():
    return render_template('spotify_download.html')

# Keresés letöltés oldal
@app.route('/zeneletolto/kereses')
def search_download():
    return render_template('search_download.html')

# YouTube letöltés endpoint
@app.route('/download/youtube', methods=['POST'])
def download_youtube():
    if request.method == 'POST':
        url = request.form.get('url')

        if not url:
            flash('Nincs URL megadva!', 'error')
            return redirect(url_for('youtube_download'))

        # YouTube URL ellenőrzése
        if 'youtube.com' not in url and 'youtu.be' not in url:
            flash('Érvényes YouTube URL-t adj meg!', 'error')
            return redirect(url_for('youtube_download'))

        try:
            from youtube_downloader import download_youtube_audio
            file_path, result = download_youtube_audio(url, DOWNLOAD_FOLDER)
        except Exception as e:
            flash(f'Hiba történt: {str(e)}', 'error')
            return redirect(url_for('youtube_download'))

        if file_path:
            # Adatok mentése adatbázisba
            try:
                conn = sqlite3.connect(DATABASE)
                c = conn.cursor()
                c.execute('INSERT INTO downloads (service, title, url, quality) VALUES (?, ?, ?, ?)',
                          ('youtube', result, url, '320kbps MP3 with Cover Art'))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Adatbázis hiba: {e}")

            # Fájl letöltése a felhasználónak
            try:
                filename = os.path.basename(file_path)
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='audio/mpeg'
                )
            except Exception as e:
                flash(f'Fájl küldési hiba: {str(e)}', 'error')
                return redirect(url_for('youtube_download'))
        else:
            flash(f'Letöltési hiba: {result}', 'error')
            return redirect(url_for('youtube_download'))

    return redirect(url_for('youtube_download'))

# Admin felület
@app.route('/admin')
def admin_panel():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('SELECT * FROM downloads ORDER BY download_date DESC')
    downloads = c.fetchall()

    c.execute('SELECT service, COUNT(*) FROM downloads GROUP BY service')
    stats = c.fetchall()

    conn.close()

    return render_template('admin.html', downloads=downloads, stats=stats)

# Letöltés törlése
@app.route('/admin/delete/<int:download_id>')
def delete_download(download_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('DELETE FROM downloads WHERE id = ?', (download_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)