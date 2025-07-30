#!/usr/bin/env python3
"""
PipePipe Metadata Tool - GUI application for managing PipePipe/NewPipe backups

This tool provides an easy-to-use interface for:
- Updating video metadata in PipePipe backups
- Cleaning unavailable videos from local playlists
- Creating updated backup files

Author: GitHub Community
License: MIT
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import zipfile
import os
import tempfile
import shutil
import subprocess
import sqlite3
import threading
from datetime import datetime
import sys

# Language texts
LANGUAGES = {
    'en': {
        'title': 'PipePipe Metadata Tool',
        'instructions': 'Upload your PipePipe backup and choose what to do',
        'files': 'Files',
        'backup_label': 'PipePipe Backup (.zip):',
        'cookies_label': 'Cookies.txt (optional):',
        'browse': 'Browse',
        'actions': 'Actions',
        'update_metadata': '🔄 Update Metadata',
        'clean_unavailable': '🧹 Clean Unavailable',
        'do_both': '✨ Do Both',
        'status': 'Status',
        'ready': 'Ready to start',
        'language': 'Language:',
        'tool_started': 'PipePipe Metadata Tool started!',
        'upload_backup': 'Upload your backup.zip to begin.',
        'backup_selected': 'Backup selected: {}',
        'cookies_selected': 'Cookies selected: {}',
        'select_backup_first': 'Select a backup file first!',
        'error': 'Error',
        'creating_workdir': 'Creating work directory: {}',
        'db_not_found': 'PipePipe.db not found in backup!',
        'settings_not_found': 'PipePipe.settings not found in backup!',
        'backup_extracted': '✓ Backup extracted successfully',
        'extract_error': 'Could not extract backup: {}',
        'updating_metadata': 'Updating metadata...',
        'metadata_updated': '✓ Metadata updated successfully!',
        'update_error': '✗ Error during update:',
        'cleaning_unavailable': 'Cleaning unavailable videos...',
        'unavailable_removed': '✓ {} unavailable videos removed!',
        'clean_error': '✗ Error: {}',
        'done': 'Done',
        'full_processing': 'Starting full processing...',
        'save_backup': 'Save updated backup',
        'backup_saved': '✓ Backup saved: {}',
        'backup_save_error': '✗ Error creating backup: {}',
        'finished': 'Finished!',
        'backup_saved_msg': 'Updated backup saved:\n{}',
        'select_pipepipe_backup': 'Select PipePipe backup',
        'select_cookies': 'Select cookies.txt',
        'zip_files': 'ZIP files',
        'text_files': 'Text files',
        'all_files': 'All files'
    },
    'sv': {
        'title': 'PipePipe Metadata Tool',
        'instructions': 'Ladda upp din PipePipe backup och välj vad du vill göra',
        'files': 'Filer',
        'backup_label': 'PipePipe Backup (.zip):',
        'cookies_label': 'Cookies.txt (valfritt):',
        'browse': 'Bläddra',
        'actions': 'Åtgärder',
        'update_metadata': '🔄 Uppdatera Metadata',
        'clean_unavailable': '🧹 Rensa Otillgängliga',
        'do_both': '✨ Gör Båda',
        'status': 'Status',
        'ready': 'Redo att börja',
        'language': 'Språk:',
        'tool_started': 'PipePipe Metadata Tool startad!',
        'upload_backup': 'Ladda upp din backup.zip för att börja.',
        'backup_selected': 'Backup vald: {}',
        'cookies_selected': 'Cookies vald: {}',
        'select_backup_first': 'Välj en backup-fil först!',
        'error': 'Fel',
        'creating_workdir': 'Skapar arbetsmapp: {}',
        'db_not_found': 'PipePipe.db hittades inte i backup!',
        'settings_not_found': 'PipePipe.settings hittades inte i backup!',
        'backup_extracted': '✓ Backup extraherad framgångsrikt',
        'extract_error': 'Kunde inte extrahera backup: {}',
        'updating_metadata': 'Uppdaterar metadata...',
        'metadata_updated': '✓ Metadata uppdaterad framgångsrikt!',
        'update_error': '✗ Fel vid uppdatering:',
        'cleaning_unavailable': 'Rensar otillgängliga videor...',
        'unavailable_removed': '✓ {} otillgängliga videor borttagna!',
        'clean_error': '✗ Fel: {}',
        'done': 'Klar',
        'full_processing': 'Startar fullständig bearbetning...',
        'save_backup': 'Spara uppdaterad backup',
        'backup_saved': '✓ Backup sparad: {}',
        'backup_save_error': '✗ Fel vid skapande av backup: {}',
        'finished': 'Klart!',
        'backup_saved_msg': 'Uppdaterad backup sparad:\n{}',
        'select_pipepipe_backup': 'Välj PipePipe backup',
        'select_cookies': 'Välj cookies.txt',
        'zip_files': 'ZIP filer',
        'text_files': 'Text filer',
        'all_files': 'Alla filer'
    }
}

class PipePipeMetadataTool:
    """
    Main application class for the PipePipe Metadata Tool.
    
    Provides a GUI interface for managing PipePipe backup files including
    metadata updates and cleanup of unavailable videos.
    """
    
    def __init__(self, root):
        """Initialize the application with the main window."""
        self.root = root
        self.root.title("PipePipe Metadata Tool")
        self.root.geometry("600x500")
        self.root.configure(bg='#f0f0f0')
        
        # Language settings - defaults to English
        self.current_language = 'en'
        
        # File path variables
        self.backup_file = tk.StringVar()
        self.cookies_file = tk.StringVar()
        self.working_dir = None
        
        # UI components that need updating when language changes
        self.ui_components = {}
        
        self.setup_ui()
        
    def get_text(self, key):
        """Get localized text for the current language."""
        return LANGUAGES[self.current_language].get(key, key)
        
    def change_language(self, event=None):
        """Change the application language and update all UI elements."""
        selected = self.language_var.get()
        if selected == 'English':
            self.current_language = 'en'
        elif selected == 'Svenska':
            self.current_language = 'sv'
        
        self.update_ui_texts()
        
    def update_ui_texts(self):
        """Update all UI text elements with current language."""
        self.root.title(self.get_text('title'))
        
        # Update labels and buttons
        if 'title_label' in self.ui_components:
            self.ui_components['title_label'].config(text=self.get_text('title'))
        if 'instructions_label' in self.ui_components:
            self.ui_components['instructions_label'].config(text=self.get_text('instructions'))
        if 'file_frame' in self.ui_components:
            self.ui_components['file_frame'].config(text=self.get_text('files'))
        if 'backup_label' in self.ui_components:
            self.ui_components['backup_label'].config(text=self.get_text('backup_label'))
        if 'cookies_label' in self.ui_components:
            self.ui_components['cookies_label'].config(text=self.get_text('cookies_label'))
        if 'browse_backup_btn' in self.ui_components:
            self.ui_components['browse_backup_btn'].config(text=self.get_text('browse'))
        if 'browse_cookies_btn' in self.ui_components:
            self.ui_components['browse_cookies_btn'].config(text=self.get_text('browse'))
        if 'action_frame' in self.ui_components:
            self.ui_components['action_frame'].config(text=self.get_text('actions'))
        if 'update_btn' in self.ui_components:
            self.ui_components['update_btn'].config(text=self.get_text('update_metadata'))
        if 'clean_btn' in self.ui_components:
            self.ui_components['clean_btn'].config(text=self.get_text('clean_unavailable'))
        if 'both_btn' in self.ui_components:
            self.ui_components['both_btn'].config(text=self.get_text('do_both'))
        if 'status_label' in self.ui_components:
            self.ui_components['status_label'].config(text=self.get_text('ready'))
        if 'log_frame' in self.ui_components:
            self.ui_components['log_frame'].config(text=self.get_text('status'))
        if 'language_label' in self.ui_components:
            self.ui_components['language_label'].config(text=self.get_text('language'))
        
    def setup_ui(self):
        """Create and configure all UI elements."""
        # Language selector at the top
        lang_frame = ttk.Frame(self.root)
        lang_frame.pack(fill='x', padx=20, pady=5)
        
        self.ui_components['language_label'] = ttk.Label(lang_frame, text=self.get_text('language'))
        self.ui_components['language_label'].pack(side='right', padx=5)
        
        self.language_var = tk.StringVar(value='English')
        language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                     values=['English', 'Svenska'], state='readonly', width=10)
        language_combo.pack(side='right')
        language_combo.bind('<<ComboboxSelected>>', self.change_language)
        
        # Main title
        self.ui_components['title_label'] = tk.Label(self.root, text=self.get_text('title'), 
                        font=("Arial", 16, "bold"), bg='#f0f0f0')
        self.ui_components['title_label'].pack(pady=10)
        
        # Instructions
        self.ui_components['instructions_label'] = tk.Label(self.root, 
                               text=self.get_text('instructions'),
                               font=("Arial", 10), bg='#f0f0f0')
        self.ui_components['instructions_label'].pack(pady=5)
        
        # File selection section
        self.ui_components['file_frame'] = ttk.LabelFrame(self.root, text=self.get_text('files'), padding=10)
        self.ui_components['file_frame'].pack(fill='x', padx=20, pady=10)
        
        # Backup file selection
        backup_row = ttk.Frame(self.ui_components['file_frame'])
        backup_row.pack(fill='x', pady=5)
        
        self.ui_components['backup_label'] = ttk.Label(backup_row, text=self.get_text('backup_label'))
        self.ui_components['backup_label'].pack(side='left')
        ttk.Entry(backup_row, textvariable=self.backup_file, width=40).pack(side='left', padx=5)
        self.ui_components['browse_backup_btn'] = ttk.Button(backup_row, text=self.get_text('browse'), 
                  command=self.browse_backup)
        self.ui_components['browse_backup_btn'].pack(side='left')
        
        # Cookies file selection (optional)
        cookies_row = ttk.Frame(self.ui_components['file_frame'])
        cookies_row.pack(fill='x', pady=5)
        
        self.ui_components['cookies_label'] = ttk.Label(cookies_row, text=self.get_text('cookies_label'))
        self.ui_components['cookies_label'].pack(side='left')
        ttk.Entry(cookies_row, textvariable=self.cookies_file, width=40).pack(side='left', padx=5)
        self.ui_components['browse_cookies_btn'] = ttk.Button(cookies_row, text=self.get_text('browse'), 
                  command=self.browse_cookies)
        self.ui_components['browse_cookies_btn'].pack(side='left')
        
        # Actions section
        self.ui_components['action_frame'] = ttk.LabelFrame(self.root, text=self.get_text('actions'), padding=10)
        self.ui_components['action_frame'].pack(fill='x', padx=20, pady=10)
        
        # Action buttons
        button_frame = ttk.Frame(self.ui_components['action_frame'])
        button_frame.pack()
        
        self.ui_components['update_btn'] = ttk.Button(button_frame, text=self.get_text('update_metadata'), 
                                    command=self.update_metadata, width=20)
        self.ui_components['update_btn'].pack(side='left', padx=5, pady=5)
        
        self.ui_components['clean_btn'] = ttk.Button(button_frame, text=self.get_text('clean_unavailable'), 
                                   command=self.clean_unavailable, width=20)
        self.ui_components['clean_btn'].pack(side='left', padx=5, pady=5)
        
        self.ui_components['both_btn'] = ttk.Button(button_frame, text=self.get_text('do_both'), 
                                  command=self.do_both, width=20)
        self.ui_components['both_btn'].pack(side='left', padx=5, pady=5)
        
        # Store button references for state management
        self.update_btn = self.ui_components['update_btn']
        self.clean_btn = self.ui_components['clean_btn']
        self.both_btn = self.ui_components['both_btn']
        
        # Progress bar for long-running operations
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=5)
        
        # Status text
        self.ui_components['status_label'] = tk.Label(self.root, text=self.get_text('ready'), 
                                    font=("Arial", 10), bg='#f0f0f0')
        self.ui_components['status_label'].pack(pady=5)
        self.status_label = self.ui_components['status_label']  # Keep reference for updates
        
        # Log area for detailed output
        self.ui_components['log_frame'] = ttk.LabelFrame(self.root, text=self.get_text('status'), padding=5)
        self.ui_components['log_frame'].pack(fill='both', expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(self.ui_components['log_frame'], height=10, 
                                                 font=("Consolas", 9))
        self.log_text.pack(fill='both', expand=True)
        
        # Initial log messages
        self.log(self.get_text('tool_started'))
        self.log(self.get_text('upload_backup'))
        
    def log(self, message):
        """Add a timestamped message to the log area."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def browse_backup(self):
        """Browse for a PipePipe backup file."""
        filename = filedialog.askopenfilename(
            title=self.get_text('select_pipepipe_backup'),
            filetypes=[(self.get_text('zip_files'), "*.zip"), (self.get_text('all_files'), "*.*")]
        )
        if filename:
            self.backup_file.set(filename)
            self.log(self.get_text('backup_selected').format(os.path.basename(filename)))
            
    def browse_cookies(self):
        """Browse for a cookies.txt file (optional for bypassing restrictions)."""
        filename = filedialog.askopenfilename(
            title=self.get_text('select_cookies'),
            filetypes=[(self.get_text('text_files'), "*.txt"), (self.get_text('all_files'), "*.*")]
        )
        if filename:
            self.cookies_file.set(filename)
            self.log(self.get_text('cookies_selected').format(os.path.basename(filename)))
            
    def extract_backup(self):
        """Extract the backup file to a temporary working directory."""
        if not self.backup_file.get():
            messagebox.showerror(self.get_text('error'), self.get_text('select_backup_first'))
            return False
            
        try:
            # Create temporary working directory
            self.working_dir = tempfile.mkdtemp()
            self.log(self.get_text('creating_workdir').format(self.working_dir))
            
            # Extract backup file
            with zipfile.ZipFile(self.backup_file.get(), 'r') as zip_ref:
                zip_ref.extractall(self.working_dir)
                
            # Verify required files exist
            db_path = os.path.join(self.working_dir, 'PipePipe.db')
            settings_path = os.path.join(self.working_dir, 'PipePipe.settings')
            
            if not os.path.exists(db_path):
                messagebox.showerror(self.get_text('error'), self.get_text('db_not_found'))
                return False
                
            if not os.path.exists(settings_path):
                messagebox.showerror(self.get_text('error'), self.get_text('settings_not_found'))
                return False
                
            self.log(self.get_text('backup_extracted'))
            return True
            
        except Exception as e:
            messagebox.showerror(self.get_text('error'), self.get_text('extract_error').format(str(e)))
            return False
            
    def update_metadata(self):
        """Start metadata update process in background thread."""
        self.run_in_background(self._update_metadata)
        
    def _update_metadata(self):
        """Update video metadata using yt-dlp (runs in background thread)."""
        if not self.extract_backup():
            return
            
        try:
            self.update_status(self.get_text('updating_metadata'))
            self.progress.start()
            
            # Create metadata update script dynamically
            update_script = """
import sqlite3
import subprocess
import time
from datetime import datetime

def get_video_metadata(url, cookies_file=None):
    \"\"\"Fetch video metadata using yt-dlp.\"\"\"
    try:
        cmd = ['yt-dlp', '--print', '%(title)s|||%(uploader)s|||%(duration)s|||%(view_count)s|||%(upload_date)s|||%(thumbnail)s', '--no-download', url]
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
                
                return {
                    'title': title,
                    'uploader': uploader,
                    'duration': duration,
                    'view_count': view_count,
                    'upload_date': upload_date,
                    'thumbnail_url': thumbnail_url
                }
        return None
    except:
        return None

# Update database with fresh metadata
conn = sqlite3.connect('PipePipe.db')
cursor = conn.cursor()

# Find videos in local playlists that need metadata updates
query = \"\"\"
SELECT DISTINCT s.uid, s.url, s.title, s.uploader 
FROM streams s 
JOIN playlist_stream_join psj ON s.uid = psj.stream_id 
JOIN playlists p ON psj.playlist_id = p.uid 
WHERE p.name IN ('Titta senare (PipePipe)', 'Videor som jag gillat (PipePipe)') 
AND s.title = 'YouTube Video' 
AND s.uploader = 'YouTube Creator'
ORDER BY s.uid
\"\"\"

cursor.execute(query)
videos_to_update = cursor.fetchall()

updated_count = 0
error_count = 0
cookies_file = COOKIES_FILE_PLACEHOLDER

for uid, url, old_title, old_uploader in videos_to_update:
    metadata = get_video_metadata(url, cookies_file)
    
    if metadata:
        update_query = \"\"\"
        UPDATE streams 
        SET title = ?, uploader = ?, duration = ?, view_count = ?, thumbnail_url = ?
        WHERE uid = ?
        \"\"\"
        
        cursor.execute(update_query, (
            metadata['title'],
            metadata['uploader'], 
            metadata['duration'],
            metadata['view_count'],
            metadata['thumbnail_url'],
            uid
        ))
        
        updated_count += 1
    else:
        error_count += 1
    
    conn.commit()
    time.sleep(0.5)  # Rate limiting

conn.close()

print(f"Updated: {updated_count}, Errors: {error_count}")
"""
            
            # Configure cookies file path in script
            cookies_placeholder = "None"
            if self.cookies_file.get():
                cookies_placeholder = f"'{self.cookies_file.get()}'"
            update_script = update_script.replace("COOKIES_FILE_PLACEHOLDER", cookies_placeholder)
            
            # Write and execute the update script
            script_path = os.path.join(self.working_dir, 'update_script.py')
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(update_script)
                
            # Run the script
            result = subprocess.run([sys.executable, script_path], 
                                  cwd=self.working_dir, 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                self.log(self.get_text('metadata_updated'))
                self.log(result.stdout)
            else:
                self.log(self.get_text('update_error'))
                self.log(result.stderr)
                
        except Exception as e:
            self.log(f"{self.get_text('update_error')} {str(e)}")
        finally:
            self.progress.stop()
            self.update_status(self.get_text('done'))
            
    def clean_unavailable(self):
        """Start cleanup process for unavailable videos in background thread."""
        self.run_in_background(self._clean_unavailable)
        
    def _clean_unavailable(self):
        """Remove unavailable videos from local playlists (runs in background thread)."""
        if not self.extract_backup():
            return
            
        try:
            self.update_status(self.get_text('cleaning_unavailable'))
            self.progress.start()
            
            # Connect to database
            db_path = os.path.join(self.working_dir, 'PipePipe.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Find videos that couldn't be updated (still have default metadata)
            query = '''
            SELECT DISTINCT s.uid, s.url
            FROM streams s 
            JOIN playlist_stream_join psj ON s.uid = psj.stream_id 
            JOIN playlists p ON psj.playlist_id = p.uid 
            WHERE p.name IN ('Titta senare (PipePipe)', 'Videor som jag gillat (PipePipe)') 
            AND s.title = 'YouTube Video' 
            AND s.uploader = 'YouTube Creator'
            '''
            
            cursor.execute(query)
            videos_to_remove = cursor.fetchall()
            
            removed_count = 0
            
            for uid, url in videos_to_remove:
                # Remove from local playlists only
                delete_query = '''
                DELETE FROM playlist_stream_join 
                WHERE stream_id = ? 
                AND playlist_id IN (
                    SELECT uid FROM playlists 
                    WHERE name IN ('Titta senare (PipePipe)', 'Videor som jag gillat (PipePipe)')
                )
                '''
                cursor.execute(delete_query, (uid,))
                
                # Check if video is used in other playlists
                check_query = 'SELECT COUNT(*) FROM playlist_stream_join WHERE stream_id = ?'
                cursor.execute(check_query, (uid,))
                remaining_references = cursor.fetchone()[0]
                
                # Only delete from streams table if not referenced elsewhere
                if remaining_references == 0:
                    cursor.execute('DELETE FROM streams WHERE uid = ?', (uid,))
                    
                removed_count += 1
                conn.commit()
                
            conn.close()
            
            self.log(self.get_text('unavailable_removed').format(removed_count))
            
        except Exception as e:
            self.log(f"{self.get_text('clean_error')} {str(e)}")
        finally:
            self.progress.stop()
            self.update_status(self.get_text('done'))
            
    def do_both(self):
        """Perform both metadata update and cleanup operations."""
        self.run_in_background(self._do_both)
        
    def _do_both(self):
        """Perform both operations and create final backup (runs in background thread)."""
        self.log(self.get_text('full_processing'))
        self._update_metadata()
        self._clean_unavailable()
        self.create_final_backup()
        
    def create_final_backup(self):
        """Create updated backup file with processed data."""
        try:
            if not self.working_dir:
                return
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"PipePipe_Updated_{timestamp}.zip"
            
            save_path = filedialog.asksaveasfilename(
                title=self.get_text('save_backup'),
                defaultextension=".zip",
                filetypes=[(self.get_text('zip_files'), "*.zip")],
                initialvalue=backup_name
            )
            
            if save_path:
                with zipfile.ZipFile(save_path, 'w') as zipf:
                    zipf.write(os.path.join(self.working_dir, 'PipePipe.db'), 'PipePipe.db')
                    zipf.write(os.path.join(self.working_dir, 'PipePipe.settings'), 'PipePipe.settings')
                    
                self.log(self.get_text('backup_saved').format(save_path))
                messagebox.showinfo(self.get_text('finished'), 
                                  self.get_text('backup_saved_msg').format(save_path))
                
        except Exception as e:
            self.log(self.get_text('backup_save_error').format(str(e)))
            
    def update_status(self, status):
        """Update the status label text."""
        self.status_label.config(text=status)
        self.root.update()
        
    def run_in_background(self, func):
        """Execute a function in a background thread to keep UI responsive."""
        # Disable action buttons during operation
        self.update_btn.config(state='disabled')
        self.clean_btn.config(state='disabled') 
        self.both_btn.config(state='disabled')
        
        def worker():
            try:
                func()
            finally:
                # Re-enable buttons when operation completes
                self.root.after(0, lambda: self.update_btn.config(state='normal'))
                self.root.after(0, lambda: self.clean_btn.config(state='normal'))
                self.root.after(0, lambda: self.both_btn.config(state='normal'))
                
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()

def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = PipePipeMetadataTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
