# pic-grab
Got bored from training your neural networks on recognising cats?
With these small python scripts you can quickly gather a sample of pictures and then manually sort them into categories.

## Grabber
The Grabber is a wget-like tool for downloading images from websites by traversing links according to configurable patterns.

### Features
- Follows links that match specified regex patterns
- Downloads files that match download patterns (default: jpg files)
- Avoids downloading duplicates
- Maintains a persistent session for efficient requests
- Can be configured to stay within the same network location or follow external links

### Usage
```
python3 main.py -h
```
to see all available command-line options:

- `-u, --url`: Starting URL(s) for the traversal
- `-d, --download`: Regex pattern(s) for files to download (default: `.*\.jpg`)
- `-f, --follow`: Regex pattern(s) for URLs to follow (default: `.*\.html`, `.*\/`)
- `-n, --no-follow`: Regex pattern(s) for URLs to NOT follow (takes precedence)
- `-t, --target`: Directory to save downloaded files (default: `fetched/`)
- `-i, --ignore-duplicates-in`: Skip downloading if file exists in these directories
- `-a, --allow-netloc-change`: Allow following links to different network locations
- `-l, --log`: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `-c, --config`: Load settings from a JSON configuration file

It is recommended to use a configuration file like:
```
python3 main.py -c grabber.cfg.json
```

### Example Configuration
See the included `grabber.cfg.json` for an example configuration:
```json
{
    "download": [".*\\.jpg"],
    "follow": [".*view-image.php.*"],
    "url": ["http://www.publicdomainpictures.net/top-images.php"],
    "target": "unsorted",
    "ignore_duplicates_in": ["ham", "spam", "unsorted"]
}
```

Make sure to gather only from sites which allow automated gathering and only such pictures which are free.

## Sorter
After you got some pictures, you may sort them using
```
python3 sorter.py -c sorter.cfg.json
```
See the example configuration file for sensible options (and key bindings in operation). The `esc` key will always get you out of the sorter. ;)

You can also specify image files or patterns to use:
```
python3 sorter.py -c sorter.cfg.json "path/to/images/*.jpg" "another/path/*.png"
```

## Installation
Install required dependencies:
```
pip install -r requirements.txt
```

## License

Copyright 2017 Sebastian Schmittner <sebastian@schmittner.pw>

<img alt="GPLV3" style="border-width:0" src="http://www.gnu.org/graphics/gplv3-127x51.png" /><br />

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
