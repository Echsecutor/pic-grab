# Project Structure

## Main Components

- `main.py` - Main application script with the Grabber class that handles URL crawling and image downloading
- `sorter.py` - Script for sorting downloaded images

## Configuration Files

- `grabber.cfg.json` - Configuration for the URL crawler
- `sorter.cfg.json` - Configuration for the image sorter
- `konanchan.myconfig.json` - Sample configuration file for a specific website

## Storage Directories

- `ham/` - Directory for sorted "good" images
- `spam/` - Directory for sorted "bad" images 
- `unsorted/` - Directory for images waiting to be sorted

## Project Files

- `requirements.txt` - Python dependencies
- `LICENSE` - Project license information
- `README.md` - Project documentation 