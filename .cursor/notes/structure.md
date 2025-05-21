# Project Structure

## Main Components

- `main.py` - Main application script for the pic-grab utility, contains the Grabber class and command-line interface
- `sorter.py` - Script for sorting images that have been downloaded

## Configuration Files

- `grabber.cfg.json` - Configuration for the pic grabber
- `sorter.cfg.json` - Configuration for the image sorter
- `konanchan.myconfig.json` - Example/specific configuration for a particular site

## Directories

- `ham/` - Directory for sorted "wanted" images
- `spam/` - Directory for sorted "unwanted" images
- `unsorted/` - Directory for images that have not been sorted yet
- `fetched/` - Default download directory (implied from code)

## Dependencies

- Dependencies are defined in `requirements.txt` 