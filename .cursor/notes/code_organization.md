# Code Organization Notes

## Grabber Class

The `Grabber` class in `main.py` is responsible for:
- Managing URL traversal queue
- Tracking visited URLs to avoid duplicates
  - Supports persisting visited URLs to a file
  - Can load visited URLs from a file on startup
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