#!/usr/bin/env python3
import sqlite3
from datetime import datetime

def remove_unavailable_videos():
    """Ta bort otillgängliga videor från lokala spellistor"""
    
    # Anslut till databasen
    conn = sqlite3.connect('newpipe.db')
    cursor = conn.cursor()
    
    print(f"Startar borttagning av otillgängliga videor - {datetime.now()}")
    
    # Hämta videor som fortfarande har standard metadata (misslyckade uppdateringar)
    query = '''
    SELECT DISTINCT s.uid, s.url, s.title, s.uploader, p.name as playlist_name
    FROM streams s 
    JOIN playlist_stream_join psj ON s.uid = psj.stream_id 
    JOIN playlists p ON psj.playlist_id = p.uid 
    WHERE p.name IN ('Titta senare (PipePipe)', 'Videor som jag gillat (PipePipe)') 
    AND s.title = 'YouTube Video' 
    AND s.uploader = 'YouTube Creator'
    ORDER BY s.uid
    '''
    
    cursor.execute(query)
    videos_to_remove = cursor.fetchall()
    
    print(f"Hittade {len(videos_to_remove)} otillgängliga videor att ta bort")
    
    removed_count = 0
    
    for uid, url, title, uploader, playlist in videos_to_remove:
        print(f"Tar bort video {uid}: {url} från {playlist}")
        
        # Ta bort från playlist_stream_join (kopplingen mellan video och spellista)
        delete_query = '''
        DELETE FROM playlist_stream_join 
        WHERE stream_id = ? 
        AND playlist_id IN (
            SELECT uid FROM playlists 
            WHERE name IN ('Titta senare (PipePipe)', 'Videor som jag gillat (PipePipe)')
        )
        '''
        
        cursor.execute(delete_query, (uid,))
        
        # Kontrollera om videon fortfarande används i andra spellistor
        check_query = '''
        SELECT COUNT(*) FROM playlist_stream_join WHERE stream_id = ?
        '''
        cursor.execute(check_query, (uid,))
        remaining_references = cursor.fetchone()[0]
        
        # Om videon inte används i några andra spellistor, ta bort den helt från streams-tabellen
        if remaining_references == 0:
            delete_stream_query = 'DELETE FROM streams WHERE uid = ?'
            cursor.execute(delete_stream_query, (uid,))
            print(f"  ✓ Video {uid} togs bort helt (inga andra referenser)")
        else:
            print(f"  ✓ Video {uid} togs bort från lokala spellistor (finns kvar i {remaining_references} andra spellistor)")
        
        removed_count += 1
        
        # Committa efter varje borttagning för säkerhet
        conn.commit()
    
    # Stäng databasanslutningen
    conn.close()
    
    print(f"\n=== SAMMANFATTNING ===")
    print(f"Borttagna videor: {removed_count}")
    print(f"Totalt bearbetade: {len(videos_to_remove)}")
    print(f"Dina lokala spellistor är nu rensade från otillgängliga videor!")

if __name__ == "__main__":
    print("Startar borttagning av otillgängliga videor från lokala spellistor...")
    
    # Fråga användaren om bekräftelse
    response = input(f"\nDetta kommer att ta bort 74 otillgängliga videor från dina lokala spellistor.\nVill du fortsätta? (ja/nej): ")
    
    if response.lower() in ['ja', 'j', 'yes', 'y']:
        remove_unavailable_videos()
        print(f"\nKlart! Tid: {datetime.now()}")
    else:
        print("Avbrutet av användaren.")
