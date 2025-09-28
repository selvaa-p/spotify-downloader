#!/usr/bin/env python3
"""
Spotify High-Quality Downloader
===============================

A professional-grade tool for downloading high-quality audio from Spotify playlists 
and individual tracks using the Spotify Web API and yt-dlp.

Features:
    - Download individual tracks or complete playlists
    - High-quality FLAC audio output (lossless)
    - Multiple audio format support (FLAC, MP3, M4A, Opus)
    - Complete metadata tagging with album artwork
    - ZIP archive creation for playlists with custom branding
    - No thumbnail downloads for cleaner file organization
    - Smart audio source selection (YouTube/YouTube Music)

Author: Selvaa P
License: MIT
Repository: https://github.com/selvaa-p/spotify-downloader
"""

import os
import re
import sys
import time
import logging
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC
from PIL import Image
import requests
from tqdm import tqdm
from colorama import Fore, Style, init

from config import Config

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('spotify_downloader.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Application metadata
__version__ = "2.0.0"
__author__ = "Selvaa P"
__license__ = "MIT"


class SpotifyDownloader:
    """
    Professional Spotify audio downloader with high-quality output support.
    
    This class provides comprehensive functionality for downloading audio content
    from Spotify URLs, including both individual tracks and complete playlists.
    All downloads are performed using yt-dlp for optimal quality and reliability.
    
    Attributes:
        spotify (spotipy.Spotify): Authenticated Spotify Web API client
        download_folder (str): Directory path for downloaded files
        
    Example:
        >>> downloader = SpotifyDownloader()
        >>> success, failed, archive = downloader.download_content(
        ...     "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd"
        ... )
        >>> print(f"Downloaded {success} tracks successfully")
    """
    
    def __init__(self) -> None:
        """
        Initialize the Spotify downloader with validated configuration.
        
        Raises:
            ValueError: If Spotify API credentials are missing or invalid
            Exception: If Spotify client initialization fails
        """
        logger.info("Initializing Spotify Downloader v%s", __version__)
        Config.validate_config()
        self.spotify = self._init_spotify()
        self.download_folder = Config.DOWNLOAD_FOLDER
        logger.info("Downloader initialized successfully")
        
    def _init_spotify(self) -> spotipy.Spotify:
        """
        Initialize and authenticate Spotify Web API client.
        
        Returns:
            spotipy.Spotify: Authenticated Spotify client instance
            
        Raises:
            Exception: If authentication fails or credentials are invalid
        """
        try:
            logger.debug("Authenticating with Spotify Web API")
            client_credentials_manager = SpotifyClientCredentials(
                client_id=Config.SPOTIFY_CLIENT_ID,
                client_secret=Config.SPOTIFY_CLIENT_SECRET
            )
            spotify_client = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            
            # Test the connection
            spotify_client.user('spotify')  # Simple API test
            logger.info("Successfully authenticated with Spotify Web API")
            return spotify_client
            
        except Exception as e:
            logger.error("Failed to initialize Spotify client: %s", e)
            raise Exception(
                f"Spotify API authentication failed: {e}\n"
                "Please check your SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file"
            ) from e
    
    def extract_spotify_id(self, url: str) -> tuple[str, str]:
        """
        Extract Spotify content ID and type from various URL formats.
        
        Supports both web URLs (open.spotify.com) and Spotify URI format.
        
        Args:
            url (str): Spotify URL or URI to parse
            
        Returns:
            tuple[str, str]: A tuple containing (content_type, content_id)
                           where content_type is 'playlist' or 'track'
                           
        Raises:
            ValueError: If URL format is not recognized or supported
            
        Examples:
            >>> downloader.extract_spotify_id("https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd")
            ('playlist', '37i9dQZF1DX0XUsuxWHRQd')
            
            >>> downloader.extract_spotify_id("spotify:track:4iV5W9uYEdYUVa79Axb7Rh")
            ('track', '4iV5W9uYEdYUVa79Axb7Rh')
        """
        url = url.strip()
        logger.debug("Extracting Spotify ID from URL: %s", url)
        
        # Handle web URLs (open.spotify.com)
        if 'open.spotify.com' in url:
            if '/playlist/' in url:
                content_id = url.split('/playlist/')[1].split('?')[0].split('#')[0]
                logger.debug("Detected playlist ID: %s", content_id)
                return ('playlist', content_id)
            elif '/track/' in url:
                content_id = url.split('/track/')[1].split('?')[0].split('#')[0]
                logger.debug("Detected track ID: %s", content_id)
                return ('track', content_id)
                
        # Handle Spotify URIs (spotify:playlist: or spotify:track:)
        elif url.startswith('spotify:'):
            if url.startswith('spotify:playlist:'):
                content_id = url.split('spotify:playlist:')[1]
                logger.debug("Detected playlist URI: %s", content_id)
                return ('playlist', content_id)
            elif url.startswith('spotify:track:'):
                content_id = url.split('spotify:track:')[1]
                logger.debug("Detected track URI: %s", content_id)
                return ('track', content_id)
        
        # If we reach here, the URL format is not supported
        error_msg = (
            f"Invalid Spotify URL format: {url}\n"
            "Supported formats:\n"
            "  - https://open.spotify.com/playlist/ID\n"
            "  - https://open.spotify.com/track/ID\n"
            "  - spotify:playlist:ID\n"
            "  - spotify:track:ID"
        )
        logger.error("URL parsing failed: %s", error_msg)
        raise ValueError(error_msg)
    
    def get_playlist_tracks(self, playlist_id: str) -> Dict:
        """Get all tracks from a Spotify playlist"""
        try:
            playlist = self.spotify.playlist(playlist_id)
            tracks = []
            
            # Get all tracks (handle pagination)
            results = self.spotify.playlist_tracks(playlist_id)
            tracks.extend(results['items'])
            
            while results['next']:
                results = self.spotify.next(results)
                tracks.extend(results['items'])
            
            return {
                'name': playlist['name'],
                'description': playlist['description'],
                'total_tracks': len(tracks),
                'tracks': tracks
            }
        except Exception as e:
            logger.error(f"Failed to get playlist tracks: {e}")
            raise
    
    def get_single_track(self, track_id: str) -> Dict:
        """Get a single track from Spotify"""
        try:
            track = self.spotify.track(track_id)
            
            # Format as a single-item playlist for consistency
            return {
                'name': f"Single Track: {track['name']}",
                'description': f"By {', '.join([artist['name'] for artist in track['artists']])}",
                'total_tracks': 1,
                'tracks': [{'track': track}]
            }
        except Exception as e:
            logger.error(f"Failed to get track: {e}")
            raise
    
    def format_track_info(self, track_item: Dict) -> Optional[Dict]:
        """Format track information for search and download"""
        track = track_item.get('track')
        if not track or track['type'] != 'track':
            return None
        
        artists = ', '.join([artist['name'] for artist in track['artists']])
        album = track['album']['name']
        name = track['name']
        duration_ms = track['duration_ms']
        release_date = track['album']['release_date']
        
        # Get album artwork
        album_art_url = None
        if track['album']['images']:
            album_art_url = track['album']['images'][0]['url']  # Highest quality
        
        return {
            'name': name,
            'artists': artists,
            'album': album,
            'duration_ms': duration_ms,
            'release_date': release_date,
            'album_art_url': album_art_url,
            'search_query': f"{artists} - {name}",
            'filename': self._sanitize_filename(f"{artists} - {name}")
        }
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        # Remove or replace invalid characters
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        # Limit length
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
        return sanitized
    
    def search_and_download_track(self, track_info: Dict) -> bool:
        """Search for and download a single track"""
        try:
            query = track_info['search_query']
            filename = track_info['filename']
            
            # Check if file already exists
            output_path = os.path.join(self.download_folder, f"{filename}.{Config.AUDIO_FORMAT}")
            if os.path.exists(output_path):
                print(f"{Fore.YELLOW}⏭️  Skipping (already exists): {filename}")
                return True
            
            print(f"{Fore.CYAN}🔍 Searching: {query}")
            
            # Try different audio sources based on configuration
            if Config.AUDIO_SOURCE.lower() == 'youtube_music':
                return self._download_from_youtube_music(track_info, output_path)
            else:
                # Default to YouTube
                return self._download_from_youtube(track_info, output_path)
                    
        except Exception as e:
            logger.error(f"Error downloading track {track_info.get('name', 'Unknown')}: {e}")
            return False
    
    def _download_from_youtube(self, track_info: Dict, output_path: str) -> bool:
        """Download track from YouTube"""
        try:
            query = track_info['search_query']
            filename = track_info['filename']
            
            # Configure yt-dlp options for this download
            ydl_opts = Config.get_ytdlp_opts()
            ydl_opts['outtmpl'] = os.path.join(self.download_folder, f"{filename}.%(ext)s")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for the track on YouTube
                search_query = f"ytsearch{Config.MAX_SEARCH_RESULTS}:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                if not info or 'entries' not in info or not info['entries']:
                    print(f"{Fore.RED}❌ No YouTube results found for: {query}")
                    return False
                
                # Find the best match (first result is usually best)
                best_match = info['entries'][0]
                
                print(f"{Fore.GREEN}⬇️  Downloading from YouTube: {best_match.get('title', 'Unknown')}")
                
                # Download the track
                ydl.download([best_match['webpage_url']])
                
                # Add metadata to the downloaded file
                self._add_metadata(output_path, track_info)
                
                print(f"{Fore.GREEN}✅ Downloaded: {filename}")
                return True
                
        except Exception as e:
            print(f"{Fore.RED}❌ YouTube download failed for {query}: {str(e)}")
            return False
    
    def _download_from_youtube_music(self, track_info: Dict, output_path: str) -> bool:
        """Download track specifically from YouTube Music"""
        try:
            query = track_info['search_query']
            filename = track_info['filename']
            
            # Configure yt-dlp options for YouTube Music
            ydl_opts = Config.get_ytdlp_opts()
            ydl_opts['outtmpl'] = os.path.join(self.download_folder, f"{filename}.%(ext)s")
            
            # YouTube Music specific search
            ydl_opts.update({
                'default_search': 'ytsearch',
                'extract_flat': False,
            })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search specifically on YouTube Music
                search_query = f"ytmusicsearch{Config.MAX_SEARCH_RESULTS}:{query}"
                
                try:
                    info = ydl.extract_info(search_query, download=False)
                except:
                    # Fallback to regular YouTube search with "music" keyword
                    search_query = f"ytsearch{Config.MAX_SEARCH_RESULTS}:{query} music official audio"
                    info = ydl.extract_info(search_query, download=False)
                
                if not info or 'entries' not in info or not info['entries']:
                    print(f"{Fore.RED}❌ No YouTube Music results found for: {query}")
                    return False
                
                # Find the best match (prioritize official audio/music videos)
                best_match = None
                for entry in info['entries']:
                    title = entry.get('title', '').lower()
                    if any(keyword in title for keyword in ['official', 'audio', 'music']):
                        best_match = entry
                        break
                
                if not best_match:
                    best_match = info['entries'][0]  # Fallback to first result
                
                print(f"{Fore.GREEN}⬇️  Downloading from YouTube Music: {best_match.get('title', 'Unknown')}")
                
                # Download the track
                ydl.download([best_match['webpage_url']])
                
                # Add metadata to the downloaded file
                self._add_metadata(output_path, track_info)
                
                print(f"{Fore.GREEN}✅ Downloaded: {filename}")
                return True
                
        except Exception as e:
            print(f"{Fore.RED}❌ YouTube Music download failed for {query}: {str(e)}")
            return False
    
    def _add_metadata(self, file_path: str, track_info: Dict):
        """Add metadata tags to the downloaded audio file"""
        try:
            if not os.path.exists(file_path):
                return
            
            # Import additional mutagen modules for different formats
            from mutagen.flac import FLAC
            from mutagen.mp4 import MP4
            from mutagen.oggvorbis import OggVorbis
            
            if file_path.endswith('.mp3'):
                # Handle MP3 files
                audio = MP3(file_path, ID3=ID3)
                
                if audio.tags is None:
                    audio.add_tags()
                
                audio.tags[TIT2] = TIT2(encoding=3, text=track_info['name'])
                audio.tags[TPE1] = TPE1(encoding=3, text=track_info['artists'])
                audio.tags[TALB] = TALB(encoding=3, text=track_info['album'])
                
                if track_info.get('release_date'):
                    year = track_info['release_date'][:4]
                    audio.tags[TDRC] = TDRC(encoding=3, text=year)
                
                # Embed album artwork
                if track_info.get('album_art_url'):
                    self._embed_album_art_mp3(audio, track_info['album_art_url'])
                
                audio.save()
                
            elif file_path.endswith('.flac'):
                # Handle FLAC files
                audio = FLAC(file_path)
                
                audio['TITLE'] = track_info['name']
                audio['ARTIST'] = track_info['artists']
                audio['ALBUM'] = track_info['album']
                
                if track_info.get('release_date'):
                    year = track_info['release_date'][:4]
                    audio['DATE'] = year
                
                # Embed album artwork for FLAC
                if track_info.get('album_art_url'):
                    self._embed_album_art_flac(audio, track_info['album_art_url'])
                
                audio.save()
                
            elif file_path.endswith('.m4a') or file_path.endswith('.mp4'):
                # Handle M4A/MP4 files
                audio = MP4(file_path)
                
                audio['\xa9nam'] = [track_info['name']]  # Title
                audio['\xa9ART'] = [track_info['artists']]  # Artist
                audio['\xa9alb'] = [track_info['album']]  # Album
                
                if track_info.get('release_date'):
                    year = track_info['release_date'][:4]
                    audio['\xa9day'] = [year]  # Year
                
                # Embed album artwork for M4A
                if track_info.get('album_art_url'):
                    self._embed_album_art_m4a(audio, track_info['album_art_url'])
                
                audio.save()
                
            elif file_path.endswith('.ogg'):
                # Handle OGG files
                audio = OggVorbis(file_path)
                
                audio['TITLE'] = [track_info['name']]
                audio['ARTIST'] = [track_info['artists']]
                audio['ALBUM'] = [track_info['album']]
                
                if track_info.get('release_date'):
                    year = track_info['release_date'][:4]
                    audio['DATE'] = [year]
                
                audio.save()
                
        except Exception as e:
            logger.warning(f"Failed to add metadata to {file_path}: {e}")
    
    def _embed_album_art_mp3(self, audio, album_art_url: str):
        """Download and embed album artwork for MP3"""
        try:
            response = requests.get(album_art_url, timeout=10)
            if response.status_code == 200:
                audio.tags[APIC] = APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=response.content
                )
        except Exception as e:
            logger.warning(f"Failed to embed album artwork: {e}")
    
    def _embed_album_art_flac(self, audio, album_art_url: str):
        """Download and embed album artwork for FLAC"""
        try:
            from mutagen.flac import Picture
            
            response = requests.get(album_art_url, timeout=10)
            if response.status_code == 200:
                picture = Picture()
                picture.type = 3  # Cover (front)
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                picture.data = response.content
                
                # Clear existing pictures and add new one
                audio.clear_pictures()
                audio.add_picture(picture)
        except Exception as e:
            logger.warning(f"Failed to embed FLAC album artwork: {e}")
    
    def _embed_album_art_m4a(self, audio, album_art_url: str):
        """Download and embed album artwork for M4A"""
        try:
            from mutagen.mp4 import MP4Cover
            
            response = requests.get(album_art_url, timeout=10)
            if response.status_code == 200:
                audio['covr'] = [MP4Cover(response.content, imageformat=MP4Cover.FORMAT_JPEG)]
        except Exception as e:
            logger.warning(f"Failed to embed M4A album artwork: {e}")
    
    def download_content(self, spotify_url: str, create_archive: bool = True) -> Tuple[int, int, Optional[str]]:
        """Download content from Spotify URL (playlist or single track)
        
        Args:
            spotify_url: Spotify URL for playlist or track
            create_archive: Whether to create ZIP archive for playlists
            
        Returns:
            tuple: (successful_downloads, failed_downloads, archive_path)
        """
        try:
            # Extract Spotify ID and type
            content_type, content_id = self.extract_spotify_id(spotify_url)
            print(f"{Fore.BLUE}📋 Getting {content_type} information...")
            
            # Get content data
            if content_type == 'playlist':
                content_data = self.get_playlist_tracks(content_id)
            elif content_type == 'track':
                content_data = self.get_single_track(content_id)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            content_name = content_data['name']
            total_tracks = content_data['total_tracks']
            
            print(f"{Fore.GREEN}🎵 {content_type.title()}: {content_name}")
            print(f"{Fore.GREEN}📊 Total tracks: {total_tracks}")
            print(f"{Fore.GREEN}📁 Download folder: {self.download_folder}")
            
            # Create temporary folder for playlist downloads
            temp_folder = None
            if content_type == 'playlist' and create_archive:
                temp_folder = os.path.join(self.download_folder, f"temp_{content_id}")
                os.makedirs(temp_folder, exist_ok=True)
                print(f"{Fore.CYAN}📦 Will create archive after download")
            
            print("-" * 50)
            
            successful_downloads = 0
            failed_downloads = 0
            downloaded_files = []
            
            # Process each track
            for i, track_item in enumerate(tqdm(content_data['tracks'], desc="Downloading tracks"), 1):
                track_info = self.format_track_info(track_item)
                
                if track_info is None:
                    print(f"{Fore.YELLOW}⏭️  Skipping invalid track {i}")
                    failed_downloads += 1
                    continue
                
                print(f"\n{Fore.BLUE}[{i}/{total_tracks}] Processing: {track_info['search_query']}")
                
                # Use temp folder for playlist downloads
                if temp_folder:
                    original_folder = self.download_folder
                    self.download_folder = temp_folder
                
                if self.search_and_download_track(track_info):
                    successful_downloads += 1
                    if temp_folder:
                        # Track the downloaded file
                        file_path = os.path.join(temp_folder, f"{track_info['filename']}.{Config.AUDIO_FORMAT}")
                        if os.path.exists(file_path):
                            downloaded_files.append(file_path)
                else:
                    failed_downloads += 1
                
                # Restore original folder
                if temp_folder:
                    self.download_folder = original_folder
                
                # Small delay to be respectful to the services
                time.sleep(1)
            
            print(f"\n{Fore.GREEN}🎉 Download Complete!")
            print(f"{Fore.GREEN}✅ Successful: {successful_downloads}")
            print(f"{Fore.RED}❌ Failed: {failed_downloads}")
            
            # Create archive for playlists
            archive_path = None
            if content_type == 'playlist' and create_archive and downloaded_files:
                archive_path = self._create_playlist_archive(content_name, temp_folder, downloaded_files)
                
                # Clean up temp folder
                if temp_folder and os.path.exists(temp_folder):
                    shutil.rmtree(temp_folder)
            
            return successful_downloads, failed_downloads, archive_path
            
        except Exception as e:
            logger.error(f"Failed to download content: {e}")
            raise
    
    def _create_playlist_archive(self, playlist_name: str, temp_folder: str, downloaded_files: List[str]) -> str:
        """Create a ZIP archive with downloaded tracks and brand logo"""
        try:
            # Sanitize playlist name for filename
            safe_name = self._sanitize_filename(playlist_name)
            archive_name = f"{safe_name}.zip"
            archive_path = os.path.join(self.download_folder, archive_name)
            
            print(f"{Fore.CYAN}📦 Creating archive: {archive_name}")
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                # Add all downloaded tracks
                for file_path in downloaded_files:
                    if os.path.exists(file_path):
                        # Use just the filename in the archive (no path)
                        filename = os.path.basename(file_path)
                        zipf.write(file_path, filename)
                
                # Create and add brand logo
                self._add_brand_logo_to_archive(zipf, playlist_name)
                
                # Add a playlist info file
                self._add_playlist_info_to_archive(zipf, playlist_name, len(downloaded_files))
            
            print(f"{Fore.GREEN}✅ Archive created: {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Failed to create archive: {e}")
            return None
    
    def _add_brand_logo_to_archive(self, zipf: zipfile.ZipFile, playlist_name: str):
        """Add a brand logo image to the archive"""
        try:
            # Create a simple brand logo using PIL
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a 512x512 image with gradient background
            img = Image.new('RGB', (512, 512), color='#1DB954')  # Spotify green
            draw = ImageDraw.Draw(img)
            
            # Add gradient effect
            for y in range(512):
                alpha = y / 512
                color = (
                    int(29 * (1 - alpha) + 25 * alpha),    # Darker green
                    int(185 * (1 - alpha) + 20 * alpha),   # Fade to dark
                    int(84 * (1 - alpha) + 25 * alpha)
                )
                draw.line([(0, y), (512, y)], fill=color)
            
            # Add text
            try:
                # Try to use a nice font
                font_large = ImageFont.truetype("arial.ttf", 48)
                font_small = ImageFont.truetype("arial.ttf", 24)
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Add app name
            draw.text((256, 200), "Spotify Downloader", font=font_large, 
                     fill='white', anchor='mm')
            
            # Add playlist name (truncated if too long)
            playlist_display = playlist_name[:30] + "..." if len(playlist_name) > 30 else playlist_name
            draw.text((256, 260), playlist_display, font=font_small, 
                     fill='white', anchor='mm')
            
            # Add download info
            draw.text((256, 320), f"Downloaded: {time.strftime('%Y-%m-%d %H:%M')}", 
                     font=font_small, fill='white', anchor='mm')
            
            # Save to bytes and add to zip
            from io import BytesIO
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG', optimize=True)
            img_bytes.seek(0)
            
            zipf.writestr("📀 Playlist Cover.png", img_bytes.getvalue())
            
        except Exception as e:
            logger.warning(f"Failed to create brand logo: {e}")
            # Add a simple text file instead
            logo_text = f"""
🎵 Spotify Downloader
==================

Playlist: {playlist_name}
Downloaded: {time.strftime('%Y-%m-%d %H:%M:%S')}

Enjoy your music! 🎶
"""
            zipf.writestr("📀 Playlist Info.txt", logo_text)
    
    def _add_playlist_info_to_archive(self, zipf: zipfile.ZipFile, playlist_name: str, track_count: int):
        """Add playlist information file to archive"""
        info_text = f"""# {playlist_name}

**Downloaded:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Total Tracks:** {track_count}  
**Audio Format:** {Config.AUDIO_FORMAT.upper()}  
**Audio Source:** {Config.AUDIO_SOURCE.title()}  

---

*Downloaded with Spotify Downloader*  
*High-quality audio preservation*

## Track List
"""
        
        zipf.writestr("ℹ️ Playlist Info.md", info_text)


def main():
    """
    Main entry point for the Spotify High-Quality Downloader.
    
    Handles command-line arguments, initializes the downloader, and manages
    the download process with proper error handling and user feedback.
    """
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description=f"Spotify High-Quality Downloader v{__version__}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Download a playlist:
    python spotify_downloader.py "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd"
  
  Download a single track:
    python spotify_downloader.py "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
  
  Using Spotify URIs:
    python spotify_downloader.py "spotify:playlist:37i9dQZF1DX0XUsuxWHRQd"

For more information, visit: https://github.com/selvaa-p/spotify-downloader
        """)
    
    parser.add_argument(
        'url',
        help='Spotify playlist or track URL/URI to download'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'Spotify High-Quality Downloader {__version__}'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--no-archive',
        action='store_true',
        help='Disable ZIP archive creation for playlists'
    )
    
    try:
        args = parser.parse_args()
    except SystemExit:
        return
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Display banner
    print(f"{Fore.MAGENTA}🎵 Spotify High-Quality Downloader v{__version__}")
    print(f"{Fore.MAGENTA}{'=' * 50}")
    print(f"{Fore.CYAN}Author: {__author__} | License: {__license__}")
    print()
    
    try:
        # Initialize downloader
        logger.info("Starting download process for URL: %s", args.url)
        downloader = SpotifyDownloader()
        
        # Determine content type and display info
        try:
            content_type, content_id = downloader.extract_spotify_id(args.url)
            logger.info("Detected %s with ID: %s", content_type, content_id)
            
            if content_type == 'playlist':
                print(f"{Fore.CYAN}📦 Playlist downloads will be archived with brand logo")
            elif content_type == 'track':
                print(f"{Fore.CYAN}🎵 Single track download")
                
        except ValueError as e:
            logger.error("URL validation failed: %s", e)
            print(f"{Fore.RED}❌ {e}")
            return 1
        
        # Start download process
        create_archive = not args.no_archive
        successful, failed, archive_path = downloader.download_content(
            args.url, 
            create_archive=create_archive
        )
        
        # Display results
        print(f"\n{Fore.GREEN}🎉 Download Summary:")
        print(f"{Fore.GREEN}  ✅ Successful: {successful}")
        if failed > 0:
            print(f"{Fore.RED}  ❌ Failed: {failed}")
        
        if archive_path:
            print(f"{Fore.GREEN}  📦 Archive: {archive_path}")
        
        logger.info("Download completed. Success: %d, Failed: %d", successful, failed)
        
        # Exit with appropriate code
        return 1 if failed > 0 else 0
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️  Download interrupted by user")
        logger.info("Download interrupted by user")
        return 0
        
    except Exception as e:
        error_msg = str(e)
        logger.error("Unexpected error occurred: %s", error_msg, exc_info=True)
        print(f"{Fore.RED}💥 Error: {error_msg}")
        print(f"{Fore.YELLOW}💡 Check the log file for detailed error information")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code or 0)
