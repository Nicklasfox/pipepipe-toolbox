# PipePipe Metadata Tool

A user-friendly GUI application for managing PipePipe/NewPipe backup files. This tool helps you update video metadata and clean up unavailable videos from your local playlists.

## Features

- **Metadata Updates**: Automatically fetch fresh metadata for videos using yt-dlp
- **Cleanup Unavailable Videos**: Remove videos that are no longer accessible from local playlists
- **Multilingual Support**: Available in English and Swedish
- **User-Friendly GUI**: Simple and intuitive interface built with Tkinter
- **Backup Management**: Create updated backup files after processing

## Screenshot

![PipePipe Metadata Tool Interface](screenshot.png)

## Requirements

- Python 3.7 or higher
- yt-dlp (automatically handled by the application)
- A PipePipe/NewPipe backup file (.zip format)

## Installation

### Option 1: Download Executable (Recommended for Windows users)
1. Download the latest release from the [Releases](../../releases) page
2. Extract the zip file
3. Run `PipePipe_Metadata_Tool.exe`

### Option 2: Run from Source
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/pipepipe-metadata-tool.git
   cd pipepipe-metadata-tool
   ```

2. Install dependencies:
   ```bash
   pip install yt-dlp
   ```

3. Run the application:
   ```bash
   python newpipe_metadata_tool.py
   ```

## Usage

1. **Select your backup file**: Click "Browse" next to "PipePipe Backup (.zip)" and select your backup file
2. **Optional: Add cookies file**: If you have a cookies.txt file for bypassing restrictions, select it
3. **Choose an action**:
   - **🔄 Update Metadata**: Fetch fresh metadata for videos with missing information
   - **🧹 Clean Unavailable**: Remove videos that can't be accessed anymore
   - **✨ Do Both**: Perform both operations and create a new backup file

## How it Works

### Metadata Updates
The tool identifies videos in your local playlists that have default metadata (title: "YouTube Video", uploader: "YouTube Creator") and attempts to fetch fresh information using yt-dlp.

### Cleanup Process
Videos that couldn't be updated (usually due to being private, deleted, or region-blocked) are removed from your local playlists while preserving them in other playlists.

### Targeted Playlists
The tool specifically works with these local playlists:
- "Titta senare (PipePipe)" (Watch Later)
- "Videor som jag gillat (PipePipe)" (Liked Videos)

## Supported Languages

- 🇬🇧 English (default)
- 🇸🇪 Svenska (Swedish)

## Technical Details

- **Database**: Works with SQLite databases from PipePipe/NewPipe
- **Video Processing**: Uses yt-dlp for metadata extraction
- **GUI Framework**: Built with Python Tkinter
- **Threading**: Background processing to keep UI responsive

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application in development mode:
   ```bash
   python newpipe_metadata_tool.py
   ```

## Building Executable

To build your own executable:

```bash
pip install pyinstaller
pyinstaller pipepipe_tool.spec
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is not affiliated with NewPipe or PipePipe. It's an independent utility created to help manage backup files. Always backup your data before using any processing tools.

## Troubleshooting

### Common Issues

**"yt-dlp not found"**
- Make sure yt-dlp is installed: `pip install yt-dlp`
- On Windows, ensure Python Scripts folder is in your PATH

**"Database not found in backup"**
- Ensure your backup file contains `PipePipe.db` and `PipePipe.settings`
- Verify the backup was created properly from PipePipe/NewPipe

**Videos not updating**
- Some videos may be region-locked, private, or deleted
- Try using a cookies.txt file for better access
- Check your internet connection

## Support

If you encounter issues or have questions:
1. Check the [Issues](../../issues) page for existing solutions
2. Create a new issue with detailed information about your problem
3. Include your Python version and operating system

---

Made with ❤️ for the NewPipe/PipePipe community
