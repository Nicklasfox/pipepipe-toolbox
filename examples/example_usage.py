#!/usr/bin/env python3
"""
Example script showing how to use PipePipe Metadata Tool programmatically
This demonstrates the core functionality without the GUI.
"""

import os
import sys
import tempfile
import zipfile
import sqlite3
import subprocess
import time

def extract_backup(backup_file, work_dir):
    """Extract PipePipe backup to working directory"""
    print(f"Extracting backup: {backup_file}")
    
    with zipfile.ZipFile(backup_file, 'r') as zip_ref:
        zip_ref.extractall(work_dir)
    
    # Verify required files
    db_path = os.path.join(work_dir, 'PipePipe.db')
    settings_path = os.path.join(work_dir, 'PipePipe.settings')
    
    if not os.path.exists(db_path):
        raise FileNotFoundError("PipePipe.db not found in backup")
    if not os.path.exists(settings_path):
        raise FileNotFoundError("PipePipe.settings not found in backup")
    
    print("✓ Backup extracted successfully")
    return db_path, settings_path

def get_video_stats(db_path):
    """Get statistics about videos in the database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Total videos
    cursor.execute("SELECT COUNT(*) FROM streams")
    total_videos = cursor.fetchone()[0]
    
    # Videos needing metadata updates
    cursor.execute("""
        SELECT COUNT(DISTINCT s.uid)
        FROM streams s 
        JOIN playlist_stream_join psj ON s.uid = psj.stream_id 
        JOIN playlists p ON psj.playlist_id = p.uid 
        WHERE p.name IN ('Titta senare (PipePipe)', 'Videor som jag gillat (PipePipe)') 
        AND s.title = 'YouTube Video' 
        AND s.uploader = 'YouTube Creator'
    """)
    needs_update = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_videos': total_videos,
        'needs_update': needs_update
    }

def update_video_metadata(db_path, cookies_file=None, max_videos=None):
    """Update metadata for videos that need it"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
    
    if max_videos:
        query += f" LIMIT {max_videos}"
    
    cursor.execute(query)
    videos_to_update = cursor.fetchall()
    
    updated_count = 0
    error_count = 0
    
    print(f"Found {len(videos_to_update)} videos to update")
    
    for i, (uid, url, old_title, old_uploader) in enumerate(videos_to_update, 1):
        print(f"Processing {i}/{len(videos_to_update)}: {url}")
        
        try:
            # Build yt-dlp command
            cmd = [
                'yt-dlp', 
                '--print', 
                '%(title)s|||%(uploader)s|||%(duration)s|||%(view_count)s|||%(upload_date)s|||%(thumbnail)s',
                '--no-download', 
                url
            ]
            
            if cookies_file:
                cmd.extend(['--cookies', cookies_file])
            
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
                    
                    # Update database
                    update_query = """
                    UPDATE streams 
                    SET title = ?, uploader = ?, duration = ?, view_count = ?, thumbnail_url = ?
                    WHERE uid = ?
                    """
                    
                    cursor.execute(update_query, (
                        title, uploader, duration, view_count, thumbnail_url, uid
                    ))
                    
                    updated_count += 1
                    print(f"  ✓ Updated: {title[:50]}...")
                else:
                    error_count += 1
                    print(f"  ✗ Invalid response format")
            else:
                error_count += 1
                print(f"  ✗ yt-dlp error: {result.stderr.strip()[:100]}")
                
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error: {str(e)}")
        
        conn.commit()
        time.sleep(0.5)  # Rate limiting
    
    conn.close()
    
    print(f"\nMetadata update complete:")
    print(f"  Updated: {updated_count}")
    print(f"  Errors: {error_count}")
    
    return updated_count, error_count

def create_backup(work_dir, output_path):
    """Create new backup file"""
    db_path = os.path.join(work_dir, 'PipePipe.db')
    settings_path = os.path.join(work_dir, 'PipePipe.settings')
    
    with zipfile.ZipFile(output_path, 'w') as zipf:
        zipf.write(db_path, 'PipePipe.db')
        zipf.write(settings_path, 'PipePipe.settings')
    
    print(f"✓ New backup created: {output_path}")

def main():
    """Example usage of the metadata update functionality"""
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py <backup_file.zip> [cookies.txt] [max_videos]")
        print("Example: python example_usage.py my_backup.zip cookies.txt 10")
        sys.exit(1)
    
    backup_file = sys.argv[1]
    cookies_file = sys.argv[2] if len(sys.argv) > 2 else None
    max_videos = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    if not os.path.exists(backup_file):
        print(f"Error: Backup file not found: {backup_file}")
        sys.exit(1)
    
    if cookies_file and not os.path.exists(cookies_file):
        print(f"Error: Cookies file not found: {cookies_file}")
        sys.exit(1)
    
    # Create temporary working directory
    with tempfile.TemporaryDirectory() as work_dir:
        try:
            # Extract backup
            db_path, settings_path = extract_backup(backup_file, work_dir)
            
            # Show initial stats
            stats = get_video_stats(db_path)
            print(f"\nDatabase statistics:")
            print(f"  Total videos: {stats['total_videos']}")
            print(f"  Need metadata update: {stats['needs_update']}")
            
            if stats['needs_update'] == 0:
                print("No videos need updating!")
                return
            
            # Update metadata
            print(f"\nStarting metadata update...")
            if max_videos:
                print(f"  Limited to {max_videos} videos")
            
            updated, errors = update_video_metadata(db_path, cookies_file, max_videos)
            
            # Create new backup
            output_file = backup_file.replace('.zip', '_updated.zip')
            create_backup(work_dir, output_file)
            
            print(f"\nProcess complete!")
            print(f"  Input: {backup_file}")
            print(f"  Output: {output_file}")
            print(f"  Updated videos: {updated}")
            print(f"  Errors: {errors}")
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
