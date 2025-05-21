# Pic-Grab Features

## URL Crawler (main.py)

The main component is a web crawler that:

- Follows links based on configurable regex patterns
- Downloads images or other files matching regex patterns
- Maintains a queue of URLs to visit
- Skips already visited URLs to avoid loops
- Persists state between sessions by saving/loading:
  - Visited URLs (to avoid revisiting)
  - URL queue (to resume crawling)
- Allows configuration via command line arguments or JSON config files
- Can restrict crawling to a specific network location

## Key Classes and Components

### Grabber Class
- Uses a deque for URL queue management
- Maintains a set of visited URLs
- Uses regular expressions to determine which URLs to follow/download
- Saves progress to files periodically to allow resuming interrupted crawls

## Configuration Options

- URL patterns to follow
- URL patterns to ignore
- File patterns to download
- Target directory for downloads
- Ability to check for duplicate files
- Customizable save frequency for visited URLs and queue 