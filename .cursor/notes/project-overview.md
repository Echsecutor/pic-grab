# Pic-Grab Project Overview

## Project Structure
- `main.py`: Main entry point for downloading images
- `sorter.py`: Tool for viewing and sorting images using tkinter UI
- `grabber.cfg.json`: Configuration for image downloader
- `sorter.cfg.json`: Configuration for image sorter key bindings
- Directories: Project has directories for sorted and unsorted images

## Key Features
### Grabber (`main.py`)
- Downloads images from configured sources
- Command-line options:
  - `-c/--config`: Specify config file path
  - Various other options available via `-h` help flag

### Sorter (`sorter.py`)
- Tkinter-based image viewer for sorting images
- Creates target directories automatically
- Handles EXIF orientation correction
- Command-line options:
  - `-c/--config`: Specify config file (default: sorter.cfg.json)
  - Optional positional arguments for image files (default: *.jpg)

## Configuration
- `sorter.cfg.json`: Contains key bindings for sorting operations
  - Default keys: ESC (QUIT), "r" (RELOAD)
- `grabber.cfg.json`: Contains URL patterns for downloading images

## UI Implementation
- Uses Tkinter with minimum window size 800x600
- Images are automatically resized to fit window
- Components:
  - ImgView class (displays images)
  - Controller class (handles user input and application logic)
- Uses Pillow 11.2.1+ with Image.Resampling.LANCZOS for image processing

## Technical Notes
- Python logging module used throughout
- Key bindings trigger actions like MOVE, COPY, NEXT, DELETE
- Snake_case naming convention for variables 