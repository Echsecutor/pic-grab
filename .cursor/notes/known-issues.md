# Known Issues & Technical Notes

## Logging Issues
- The `logging` module functions do not support the `end` parameter like Python's `print()`
- Solution: Use string formatting or concatenation instead
- Example: Change `logging.info("Moving", end=" ")` to `logging.info("Moving")`

## Pillow Compatibility
- Project uses Pillow 11.2.1+
- `Image.ANTIALIAS` has been replaced with `Image.Resampling.LANCZOS` in newer versions 