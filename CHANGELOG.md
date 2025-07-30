# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-30

### Added
- Initial release of PipePipe Metadata Tool
- GUI application for managing PipePipe/NewPipe backups
- Metadata update functionality using yt-dlp
- Cleanup of unavailable videos from local playlists
- Multilingual support (English and Swedish)
- Background processing with progress indication
- Automatic backup creation after processing
- Support for cookies.txt files for enhanced access
- Cross-platform compatibility (Windows executable included)

### Features
- **Update Metadata**: Fetch fresh metadata for videos with missing information
- **Clean Unavailable**: Remove inaccessible videos from local playlists
- **Combined Processing**: Perform both operations in sequence
- **User-Friendly Interface**: Simple and intuitive GUI built with Tkinter
- **Safe Processing**: Works on temporary copies, preserves original data
- **Detailed Logging**: Real-time progress updates and detailed operation logs

### Technical Details
- Built with Python 3.7+ compatibility
- Uses yt-dlp for video metadata extraction
- SQLite database operations for PipePipe/NewPipe data
- Threaded operations to maintain UI responsiveness
- PyInstaller configuration for standalone executable creation

### Supported Platforms
- Windows (standalone .exe provided)
- Linux (Python source)
- macOS (Python source)

### Known Limitations
- Only processes local playlists: "Titta senare (PipePipe)" and "Videor som jag gillat (PipePipe)"
- Some videos may remain inaccessible due to region restrictions, privacy settings, or deletion
- Requires internet connection for metadata updates
