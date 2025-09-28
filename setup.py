#!/usr/bin/env python3
"""
Setup script for Spotify High-Quality Downloader
"""

from setuptools import setup, find_packages
import re
import os

# Read version from main module
def get_version():
    with open('spotify_downloader.py', 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    raise RuntimeError('Unable to find version string')

# Read long description from README
def get_long_description():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements from requirements.txt
def get_requirements():
    requirements = []
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = [
                line.strip() 
                for line in f 
                if line.strip() and not line.startswith('#')
            ]
    return requirements

setup(
    name='spotify-high-quality-downloader',
    version=get_version(),
    author='Selvaa P',
    author_email='cyberflixnetwork@gmail.com',
    description='A professional-grade tool for downloading high-quality audio from Spotify',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/selvaa-p/spotify-downloader',
    py_modules=['spotify_downloader', 'config'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Environment :: Console',
    ],
    keywords='spotify downloader music audio flac high-quality playlist',
    python_requires='>=3.7',
    install_requires=get_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
            'pre-commit>=2.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'spotify-downloader=spotify_downloader:main',
            'spotify-dl=spotify_downloader:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/selvaa-p/spotify-downloader/issues',
        'Source': 'https://github.com/selvaa-p/spotify-downloader',
        'Documentation': 'https://github.com/selvaa-p/spotify-downloader#readme',
        'Changelog': 'https://github.com/selvaa-p/spotify-downloader/blob/main/CHANGELOG.md',
    },
    include_package_data=True,
    zip_safe=False,
)
