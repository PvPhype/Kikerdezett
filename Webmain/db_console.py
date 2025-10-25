# db_console.py - Adatbázis kezelő konzol WebStorm-hoz
import sqlite3
from datetime import datetime

def show_downloads():
    """Összes letöltés megjelenítése"""
    conn = sqlite3.connect('music_downloader.db')
    c = conn.cursor()

    c.execute('SELECT * FROM downloads ORDER BY download_date DESC')
    downloads = c.fetchall()

    print("\n" + "="*80)
    print("ÖSSZES LETÖLTÉS")
    print("="*80)

    for download in downloads:
        print(f"ID: {download[0]}")
        print(f"Szolgáltatás: {download[1]}")
        print(f"Cím: {download[2]}")
        print(f"URL: {download[3]}")
        print(f"Minőség: {download[4]}")
        print(f"Dátum: {download[5]}")
        print("-" * 40)

    conn.close()
    return len(downloads)

def show_statistics():
    """Statisztikák megjelenítése"""
    conn = sqlite3.connect('music_downloader.db')
    c = conn.cursor()

    # Összes letöltés
    c.execute('SELECT COUNT(*) FROM downloads')
    total = c.fetchone()[0]

    # Szolgáltatásonként
    c.execute('SELECT service, COUNT(*) FROM downloads GROUP BY service')
    by_service = c.fetchall()

    # Legutóbbi letöltés
    c.execute('SELECT * FROM downloads ORDER BY download_date DESC LIMIT 1')
    latest = c.fetchone()

    print("\n" + "="*80)
    print("STATISZTIKÁK")
    print("="*80)
    print(f"Összes letöltés: {total}")
    print("\nSzolgáltatásonként:")
    for service, count in by_service:
        print(f"  {service}: {count} db")

    if latest:
        print(f"\nLegutóbbi letöltés:")
        print(f"  Cím: {latest[2]}")
        print(f"  Dátum: {latest[5]}")

    conn.close()

def delete_download(download_id):
    """Letöltés törlése ID alapján"""
    conn = sqlite3.connect('music_downloader.db')
    c = conn.cursor()

    c.execute('DELETE FROM downloads WHERE id = ?', (download_id,))
    conn.commit()

    if c.rowcount > 0:
        print(f"Letöltés #{download_id} törölve")
    else:
        print(f"Letöltés #{download_id} nem található")

    conn.close()

def clear_all_downloads():
    """Összes letöltés törlése"""
    conn = sqlite3.connect('music_downloader.db')
    c = conn.cursor()

    c.execute('DELETE FROM downloads')
    conn.commit()

    print("Összes letöltés törölve")
    conn.close()

# Használat:
if __name__ == "__main__":
    print("Adatbázis kezelő konzol - Ki kérdezett?")
    print("="*50)
    print("1 - Összes letöltés megjelenítése")
    print("2 - Statisztikák")
    print("3 - Letöltés törlése")
    print("4 - Összes letöltés törlése")
    print("0 - Kilépés")

    while True:
        try:
            choice = input("\nVálassz opciót (0-4): ")

            if choice == "1":
                count = show_downloads()
                print(f"\nÖsszesen: {count} letöltés")
            elif choice == "2":
                show_statistics()
            elif choice == "3":
                download_id = input("Add meg a törlendő letöltés ID-ját: ")
                delete_download(int(download_id))
            elif choice == "4":
                confirm = input("Biztosan törölni akarod az ÖSSZES letöltést? (igen/nem): ")
                if confirm.lower() == 'igen':
                    clear_all_downloads()
                else:
                    print("Törlés megszakítva")
            elif choice == "0":
                print("Kilépés...")
                break
            else:
                print("Érvénytelen választás")
        except ValueError:
            print("Kérlek számot adj meg!")
        except Exception as e:
            print(f"Hiba történt: {e}")