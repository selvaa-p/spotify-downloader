#!/usr/bin/env python3
"""
Configuration Management for Spotify High-Quality Downloader
==========================================================

This module handles all configuration settings for the Spotify downloader,
including environment variable loading, validation, and yt-dlp options generation.

Author: Selvaa P
License: MIT
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for Spotify High-Quality Downloader.
    
    This class manages all configuration settings including API credentials,
    download preferences, and yt-dlp options. All settings can be overridden
    via environment variables in a .env file.
    
    Attributes:
        SPOTIFY_CLIENT_ID (str): Spotify Web API client ID
        SPOTIFY_CLIENT_SECRET (str): Spotify Web API client secret
        DOWNLOAD_FOLDER (str): Directory path for downloaded files
        AUDIO_FORMAT (str): Target audio format (flac, mp3, m4a, opus)
        AUDIO_QUALITY (str): Audio quality preference
        AUDIO_SOURCE (str): Audio source preference (youtube, youtube_music)
        YTDLP_FORMAT (str): yt-dlp format selection string
    """
    
    # Spotify Web API credentials (required)
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    # Download configuration
    DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', './downloads')
    AUDIO_FORMAT = os.getenv('AUDIO_FORMAT', 'flac')  # flac, mp3, m4a, opus
    AUDIO_QUALITY = os.getenv('AUDIO_QUALITY', 'best')  # best, 320, 256, 192, 128
    AUDIO_SOURCE = os.getenv('AUDIO_SOURCE', 'youtube')  # youtube, youtube_music
    
    # yt-dlp format selection - prioritize audio-only streams
    YTDLP_FORMAT = 'bestaudio[acodec!=none]/best[height<=720]'
    
    @classmethod
    def get_ytdlp_opts(cls):
        """Get yt-dlp options based on audio format"""
        base_opts = {
            'format': cls.YTDLP_FORMAT,
            'outtmpl': f'{cls.DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'extractaudio': True,
            'embed_thumbnail': False,  # Disabled thumbnail embedding
            'writethumbnail': False,   # Disabled thumbnail download
            'writeinfojson': False,
            'ignoreerrors': True,
            'no_warnings': False,
        }
        
        # Configure based on desired audio format
        if cls.AUDIO_FORMAT.lower() == 'flac':
            base_opts.update({
                'audioformat': 'flac',
                'audioquality': '0',  # Lossless
                'prefer_free_formats': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'flac',
                    'preferredquality': '0',
                }],
            })
        elif cls.AUDIO_FORMAT.lower() == 'mp3':
            base_opts.update({
                'audioformat': 'mp3',
                'audioquality': '0' if cls.AUDIO_QUALITY == 'best' else cls.AUDIO_QUALITY,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0' if cls.AUDIO_QUALITY == 'best' else cls.AUDIO_QUALITY,
                }],
            })
        elif cls.AUDIO_FORMAT.lower() == 'm4a':
            base_opts.update({
                'audioformat': 'm4a',
                'audioquality': '0',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'aac',
                    'preferredquality': '0',
                }],
            })
        elif cls.AUDIO_FORMAT.lower() == 'opus':
            base_opts.update({
                'audioformat': 'opus',
                'audioquality': '0',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'opus',
                    'preferredquality': '0',
                }],
            })
        else:
            # Default to best available
            base_opts.update({
                'audioquality': '0',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'flac',
                    'preferredquality': '0',
                }],
            })
        
        return base_opts
    
    # Search settings
    MAX_SEARCH_RESULTS = 5
    AUDIO_SOURCE = os.getenv('AUDIO_SOURCE', 'youtube')  # youtube, youtube_music
    SEARCH_PROVIDERS = ['youtube', 'youtube music', 'tidal']
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if not cls.SPOTIFY_CLIENT_ID or not cls.SPOTIFY_CLIENT_SECRET:
            raise ValueError("Spotify API credentials are required. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file")
        
        # Create download folder if it doesn't exist
        os.makedirs(cls.DOWNLOAD_FOLDER, exist_ok=True)
