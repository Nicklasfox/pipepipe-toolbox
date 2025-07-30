#!/usr/bin/env python3
import sqlite3
import subprocess
import json
import sys
import time
from datetime import datetime

def get_video_metadata(url):
    """Hämta metadata för en video med yt-dlp"""
    try:
        cmd = [
            'yt-dlp', 
            '--print', '%(title)s|||%(uploader)s|||%(duration)s|||%(view_count)s|||%(upload_date)s|||%(thumbnail)s',
            '--no-download',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            parts = output.split('|||')
            
            if len(parts) >= 4:
                title = parts[0] if parts[0] and parts[0] != 'NA' else "YouTube Video"
                uploader = parts[1] if parts[1] and parts[1] != 'NA' else "YouTube Creator"
                duration = int(parts[2]) if parts[2] and parts[2] != 'NA' and parts[2].isdigit() else 0
                view_count = int(parts[3]) if parts[3] and parts[3] != 'NA' and parts[3].isdigit() else None
                upload_date = parts[4] if len(parts) > 4 and parts[4] and parts[4] != 'NA' else None
                thumbnail_url = parts[5] if len(parts) > 5 and parts[5] and parts[5] != 'NA' else None
                
                return {
                    'title': title,
                    'uploader': uploader,
                    'duration': duration,
                    'view_count': view_count,
                    'upload_date': upload_date,
                    'thumbnail_url': thumbnail_url
                }
        
        print(f"Fel vid hämtning av metadata för {url}: {result.stderr}")
        return None
        
    except subprocess.TimeoutExpired:
        print(f"Timeout för {url}")
        return None
    except Exception as e:
        print(f"Fel för {url}: {e}")
        return None

def update_database():
    """Uppdatera databasen med korrekt metadata"""
    
    # Anslut till databasen
    conn = sqlite3.connect('newpipe.db')
    cursor = conn.cursor()
    
    # Hämta alla videor som behöver uppdateras
    query = """
    SELECT DISTINCT s.uid, s.url, s.title, s.uploader 
    FROM streams s 
    JOIN playlist_stream_join psj ON s.uid = psj.stream_id 
    JOIN playlists p ON psj.playlist_id = p.uid 
    WHERE p.name IN ('Titta senare (PipePipe)', 'Videor som jag gillat (PipePipe)') 
    AND s.title = 'YouTube Video' 
    AND s.uploader = 'YouTube Creator'
    ORDER BY s.uid
    """
    
    cursor.execute(query)
    videos_to_update = cursor.fetchall()
    
    print(f"Hittade {len(videos_to_update)} videor som behöver uppdateras")
    
    updated_count = 0
    error_count = 0
    
    for uid, url, old_title, old_uploader in videos_to_update:
        print(f"\nBearbetar video {uid}: {url}")
        
        # Hämta metadata
        metadata = get_video_metadata(url)
        
        if metadata:
            # Uppdatera databasen
            update_query = """
            UPDATE streams 
            SET title = ?, uploader = ?, duration = ?, view_count = ?, thumbnail_url = ?
            WHERE uid = ?
            """
            
            cursor.execute(update_query, (
                metadata['title'],
                metadata['uploader'], 
                metadata['duration'],
                metadata['view_count'],
                metadata['thumbnail_url'],
                uid
            ))
            
            print(f"  ✓ Uppdaterad: '{metadata['title']}' av '{metadata['uploader']}'")
            updated_count += 1
            
        else:
            print(f"  ✗ Kunde inte hämta metadata för {url}")
            error_count += 1
        
        # Committa efter varje uppdatering för säkerhet
        conn.commit()
        
        # Kort paus för att inte överbelasta YouTube
        time.sleep(0.5)
    
    # Stäng databasanslutningen
    conn.close()
    
    print(f"\n=== SAMMANFATTNING ===")
    print(f"Uppdaterade videor: {updated_count}")
    print(f"Fel: {error_count}")
    print(f"Totalt bearbetade: {len(videos_to_update)}")

if __name__ == "__main__":
    print("Startar uppdatering av video metadata...")
    print(f"Tid: {datetime.now()}")
    
    update_database()
    
    print(f"\nKlart! Tid: {datetime.now()}")
