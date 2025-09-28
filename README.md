# 🎵 Spotify High-Quality Downloader

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://img.shields.io/github/downloads/selvaa-p/spotify-downloader/total.svg)](https://github.com/selvaa-p/spotify-downloader/releases)

> A professional-grade command-line tool for downloading high-quality audio from Spotify playlists and tracks.

## ✨ Features

- 🎯 **Lossless Quality**: Download in FLAC format for perfect audio reproduction
- 🎵 **Dual Support**: Handle both individual tracks and complete playlists
- 📦 **Smart Archiving**: Automatic ZIP creation for playlists with custom branding
- 🏷️ **Complete Metadata**: Embedded artist, album, track info, and release dates
- 🚫 **No Thumbnails**: Clean audio files without unnecessary image downloads
- 🔄 **Resume Support**: Skip already downloaded files when rerunning
- 🎨 **Professional Output**: Beautiful console interface with progress tracking
- 🌐 **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+** - [Download Python](https://python.org/downloads/)
- **FFmpeg** - Required for audio conversion
- **Spotify Developer Account** - [Get API credentials](https://developer.spotify.com/dashboard/)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/selvaa-p/spotify-downloader.git
   cd spotify-downloader
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**
   
   **Windows:**
   ```bash
   # Using chocolatey
   choco install ffmpeg
   
   # Or download from https://ffmpeg.org/download.html
   ```
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update && sudo apt install ffmpeg
   ```

4. **Configure API credentials**
   ```bash
   # Copy the example environment file
   cp env_example.txt .env
   
   # Edit .env with your Spotify API credentials
   nano .env
   ```

### Configuration

Add your Spotify API credentials to the `.env` file:

```env
# Spotify API Credentials (Required)
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# Download Settings (Optional)
DOWNLOAD_FOLDER=./downloads
AUDIO_FORMAT=flac
AUDIO_QUALITY=best
AUDIO_SOURCE=youtube_music
```

**Get Spotify API Credentials:**
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Create a new app
3. Copy your Client ID and Client Secret

## 📖 Usage

### Download Individual Tracks
```bash
python spotify_downloader.py "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
```

### Download Complete Playlists
```bash
python spotify_downloader.py "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd"
```

### Supported URL Formats
- Web URLs: `https://open.spotify.com/playlist/ID`
- Web URLs: `https://open.spotify.com/track/ID` 
- Spotify URIs: `spotify:playlist:ID`
- Spotify URIs: `spotify:track:ID`

## 🎛️ Configuration Options

| Setting | Description | Options | Default |
|---------|-------------|---------|---------|
| `AUDIO_FORMAT` | Output audio format | `flac`, `mp3`, `m4a`, `opus` | `flac` |
| `AUDIO_SOURCE` | Download source | `youtube`, `youtube_music` | `youtube_music` |
| `AUDIO_QUALITY` | Quality preference | `best`, `320`, `256`, `192`, `128` | `best` |
| `DOWNLOAD_FOLDER` | Output directory | Any valid path | `./downloads` |

## 📁 Output Structure

### Single Track Download
```
downloads/
└── Artist Name - Track Title.flac
```

### Playlist Download (ZIP Archive)
```
downloads/
└── Playlist Name.zip
    ├── Track 01 - Artist Name.flac
    ├── Track 02 - Another Artist.flac
    ├── ...
    ├── 📀 Playlist Cover.png          # Custom brand logo
    └── ℹ️ Playlist Info.md            # Download metadata
```

## 🎨 Archive Features

Playlist downloads include professional branding:

- **Custom Logo**: 512x512 PNG with Spotify-inspired design
- **Metadata File**: Markdown document with download information
- **Organized Structure**: Clean file organization within ZIP
- **Timestamp**: Download date and time for reference

## 🛠️ Development

### Project Structure
```
spotify-downloader/
├── spotify_downloader.py      # Main application
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── env_example.txt           # Environment template
├── README.md                 # Documentation
└── .env                      # Your credentials (create this)
```

### Code Quality
- **Type Hints**: Full type annotation support
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Robust exception management
- **Logging**: Professional logging with file output

### Running Tests
```bash
# Test with a single track
python spotify_downloader.py "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"

# Test with a small playlist
python spotify_downloader.py "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd"
```

## 🔧 Troubleshooting

### Common Issues

**1. FFmpeg not found**
```bash
# Verify FFmpeg installation
ffmpeg -version

# If not installed, see installation section above
```

**2. Spotify API errors**
- Verify your `.env` file has correct credentials
- Check that your Spotify app is active in the developer dashboard

**3. Download failures**
- Some tracks may not be available on YouTube
- The tool will skip unavailable tracks and continue

**4. Permission errors**
```bash
# Install packages for current user only
pip install --user -r requirements.txt
```

### Getting Help

1. Check the [Issues](https://github.com/selvaa-p/spotify-downloader/issues) page
2. Enable debug logging by adding `--debug` flag
3. Review the log file: `spotify_downloader.log`

## ⚖️ Legal Notice

**Important**: This tool is for personal use only. Please ensure you:

- ✅ Have the legal right to download the content
- ✅ Comply with Spotify's Terms of Service
- ✅ Respect local copyright laws
- ✅ Use downloads for personal, non-commercial purposes only

The developers are not responsible for any misuse of this software.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
```bash
# Clone your fork
git clone https://github.com/selvaa-p/spotify-downloader.git
cd spotify-downloader

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Spotipy](https://spotipy.readthedocs.io/) - Spotify Web API wrapper
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Media downloading capabilities
- [Mutagen](https://mutagen.readthedocs.io/) - Audio metadata handling

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=selvaa-p/spotify-downloader&type=Date)](https://star-history.com/#selvaa-p/spotify-downloader&Date)

---

**Made with ❤️ for music lovers everywhere**

*If you find this project useful, please consider giving it a star! ⭐*