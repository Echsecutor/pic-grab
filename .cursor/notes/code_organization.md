# Code Organization Notes

## Grabber Class

The `Grabber` class in `main.py` is responsible for:
- Managing URL traversal queue
- Tracking visited URLs to avoid duplicates
  - Supports persisting visited URLs to a file
  - Can load visited URLs from a file on startup
  - Periodically saves visited URLs during execution
- Following URLs based on regex patterns
- Downloading files based on regex patterns
- Checking for duplicate files

## Command Line Interface

- Argument parsing is extracted into a separate `parse_arguments()` function that returns both the parser and parsed args
- This design allows the main function to display the correct help message when needed
- Main function configures logging, initializes the grabber, and runs the main processing loop
- The application handles keyboard interrupts gracefully
  - Saves visited URLs on interrupt

## Configuration Management

The application can be configured through:
- Command line arguments
- Configuration file (JSON format)
- Command line arguments have precedence for the URL
- Other configuration parameters from the file take precedence over command line arguments
- Supports persisting visited URLs to a file (specified in config or defaults to config filename + '.visited')
- Configurable frequency for saving visited URLs during execution (default: 100)

## Main.py Structure

- `Grabber` class: Main class for crawling websites and downloading images
  - `__init__`: Initializes session, queue, and config
  - `process_found_url`: Processes URLs to determine if they should be followed or files downloaded 
  - `visit_next_url`: Retrieves the next URL and finds more URLs in the content
  - `load_visited_urls`/`save_visited_urls`: Persistence for visited URLs
  - `load_url_queue`/`save_url_queue`: Persistence for URL queue

- `parse_arguments`: Command line argument parsing
- `main`: Entry point, configures the Grabber and starts crawling

## Error Handling

- HTTP requests have status code checking with `response.ok`
- Error messages include HTTP status codes for debugging
- Connection errors are caught and logged
- Keyboard interrupts save state before exiting

## Sorter.py Structure

- `ImageView`: Displays images with proper scaling
- `Controller`: Handles user input and image operations
- Command-line interface similar to main.py

## Code Patterns

- Regular expressions for URL filtering
- JSON for configuration
- Python logging module for consistent logging
- Deque for URL queue management
- Sets for tracking visited URLs 