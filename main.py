#!/usr/bin/python3
"""This is a small command line utility to grab pictures from a web
site/gui to view them locally. Which links to follow and what to
download can be configured using regular expressions.

.. module:: pic-grab

.. moduleauthor:: Sebastian Schmittner <sebastian@schmittner.pw>


Copyright 2017 Sebastian Schmittner

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

"""

import hashlib
import json
import logging
import os
import requests
import re
import sys
import time
import random
from urllib.parse import urlparse, urljoin

from collections import deque


class Grabber(object):

    def __init__(self):
            self.url_follow_queue = deque()
            "pool of urls to visit next"

            self.visited_urls = set()
            "do not visit those again"

            self.session = requests.Session()
            "use a persistant session"

            self.config = {}
            """Holds the configuration as loaded from
            a json file, command line or defaults."""
            
            self.visited_file = None
            "Path to the file storing visited URLs"
            
            self.queue_file = None
            "Path to the file storing URL queue"

    def load_visited_urls(self):
        """Load the set of visited URLs from a file if it exists."""
        if self.visited_file and os.path.isfile(self.visited_file):
            try:
                with open(self.visited_file, 'r') as f:
                    self.visited_urls = set(json.load(f))
                logging.info("Loaded %d visited URLs from %s", len(self.visited_urls), self.visited_file)
            except Exception as e:
                logging.error("Error loading visited URLs from %s: %s", self.visited_file, e)
                
    def save_visited_urls(self):
        """Save the set of visited URLs to a file."""
        if self.visited_file:
            try:
                with open(self.visited_file, 'w') as f:
                    json.dump(list(self.visited_urls), f)
                logging.info("Saved %d visited URLs to %s", len(self.visited_urls), self.visited_file)
            except Exception as e:
                logging.error("Error saving visited URLs to %s: %s", self.visited_file, e)
                
    def load_url_queue(self):
        """Load the URL queue from a file if it exists."""
        if self.queue_file and os.path.isfile(self.queue_file):
            try:
                with open(self.queue_file, 'r') as f:
                    self.url_follow_queue = deque(json.load(f))
                logging.info("Loaded %d queued URLs from %s", len(self.url_follow_queue), self.queue_file)
            except Exception as e:
                logging.error("Error loading URL queue from %s: %s", self.queue_file, e)
                
    def save_url_queue(self):
        """Save the URL queue to a file."""
        if self.queue_file:
            try:
                with open(self.queue_file, 'w') as f:
                    json.dump(list(self.url_follow_queue), f)
                logging.info("Saved %d queued URLs to %s", len(self.url_follow_queue), self.queue_file)
            except Exception as e:
                logging.error("Error saving URL queue to %s: %s", self.queue_file, e)

    def process_found_url(self, url):
        """
        Check whether the url should be followed or downloaded.
        If so, add it to the queue or safe the file.
        """

        if url in self.visited_urls:
            logging.debug("already visited: %s", url)
            return
        self.visited_urls.add(url)

        logging.debug("processing %s", url)

        may_follow = True
        for regex_pattern in self.config["no_follow"]:
            if re.match(regex_pattern, url):
                logging.debug("will NOT follow: %s (matches %s)", url, regex_pattern)
                may_follow = False
                break

        if may_follow:
            for regex_pattern in self.config["follow"]:
                if re.match(regex_pattern, url):
                    self.url_follow_queue.append(url)
                    logging.debug("will follow: %s (matches %s)", url, regex_pattern)
                    break

        for regex_pattern in self.config["download"]:
            if re.match(regex_pattern, url):
                filename = os.path.basename(urlparse(url).path)
                logging.debug("url %s eligible for download (matches %s)", url, regex_pattern)
                # os might have filename length restrictions
                if len(filename) > 64:
                    name, extension = os.path.splitext(filename)
                    filename = hashlib.md5(name.encode()).hexdigest() + extension
                output_path = self.config["target"] + "/" + filename
                for directory in self.config["ignore_duplicates_in"]:
                    if os.path.isfile(directory + "/" + filename):
                        logging.warning("File %s exists. Skipping.", filename)
                        return

                logging.info("Downloading %s", url)
                response = self.session.get(url)
                if not response.ok:
                    logging.error("Error fetching file %s. Status code: %d", url, response.status_code)
                    return

                with open(output_path, 'wb') as output_file:
                    output_file.write(response.content)

    def visit_next_url(self):
        """
        Pop the next url, retrieve it and scan the content for further links.
        """

        url = self.url_follow_queue.popleft()
        
        response = self.session.get(url)
        if response.status_code == 503:
            logging.info("Received 503 Service Unavailable for %s. Retrying after delay...", url)
            time.sleep(random.uniform(0.1, 0.5))  # Wait 100-500ms
            response = self.session.get(url)  # Retry once
        
        if not response.ok:
            logging.error("Error fetching URL %s. Status code: %d", url, response.status_code)
            return

        # find more urls
        for match in re.finditer(
                r"""(https?://[^\s<>'"]+)|href=['"]([^"']+)|src=['"]([^"']+)""",
                response.text):
            for group in match.groups():
                if group:
                    logging.debug("raw link %s", group)
                    new_url = urljoin(url, group)
                    logging.debug("corrected link %s", new_url)
                    if urlparse(new_url).netloc != urlparse(url).netloc:
                        logging.debug("netloc change")
                        if not self.config["allow_netloc_change"]:
                            logging.debug("not following to different netloc")
                            continue
                    self.process_found_url(new_url)


def parse_arguments():
    """Parse command line arguments and return both the parser and parsed args."""
    import argparse

    parser = argparse.ArgumentParser(
        description="wget like website mirroring.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-u",
        "--url",
        nargs="*",
        help="Url(s) to start the traversal.")

    parser.add_argument(
        "-d",
        "--download",
        nargs="*",
        help="regex(s) for files to download.",
        default=[r".*\.jpg"])

    parser.add_argument(
        "-f",
        "--follow",
        nargs="*",
        help="regex(s) for urls to follow.",
        default=[r".*\.html", r".*/"])

    parser.add_argument(
        "-i",
        "--ignore-duplicates-in",
        nargs="*",
        help="If a file with the same name exists in one of these folders, skip it..",
        default=["fetched/"])

    parser.add_argument(
        "-n",
        "--no-follow",
        nargs="*",
        help="regex(s) for urls to NOT follow (takes precedence over follow).",
        default=[r".*\.jpg"])

    parser.add_argument(
        "-t",
        "--target",
        help="The directory to hold the resulting files.",
        default="fetched/")

    parser.add_argument(
        "-a",
        "--allow-netloc-change",
        help="If given (or set to True in config file) follow links" +
        " to network locations different from the starting url.",
        action='store_true')

    parser.add_argument(
        "-l",
        "--log",
        help="Set the log level.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO")

    parser.add_argument(
        "-c",
        "--config",
        help="Read config from JSON file."
        + " For the url, the command line takes precedence."
        + " For all other arguments, the config file wins.")
        
    parser.add_argument(
        "--visited-file",
        help="File to store visited URLs. Defaults to config filename + '.visited'.")
        
    parser.add_argument(
        "--queue-file",
        help="File to store URL queue. Defaults to config filename + '.queue'.")

    parser.add_argument(
        "--save-frequency",
        type=int,
        help="How often to save visited URLs and queue (number of URLs processed). Default is 100.",
        default=100)

    args = parser.parse_args()
    return parser, args


def main():
    """The main function gets a list of all mailing lists on the given
    server and performs (an) action(s) on all lists.

    """
    logger_config = {
        "level":
        logging.INFO,
        "format":
        "%(asctime)s %(funcName)s (%(lineno)d) [%(levelname)s]:    %(message)s"
    }

    parser, args = parse_arguments()

    logger_config["level"] = getattr(logging, args.log)
    logging.basicConfig(**logger_config)

    print("Log messages above level: {}".format(logger_config["level"]))

    grabber = Grabber()

    if args.config:
        with open(args.config, "r") as config_file:
            grabber.config = json.load(config_file)
            
        # Set default visited file based on config filename if not specified
        if not grabber.config.get("visited_file", None) and not args.visited_file:
            grabber.config["visited_file"] = args.config + ".visited"
            
        # Set default queue file based on config filename if not specified
        if not grabber.config.get("queue_file", None) and not args.queue_file:
            grabber.config["queue_file"] = args.config + ".queue"

    if args.url:
        grabber.config["url"] = args.url

    if not grabber.config.get("url", None):
        logging.critical("No base url(s) given.")
        parser.print_help()
        sys.exit(1)
    else:
        logging.info("url: '%s'", grabber.config["url"])

    for arg_name, arg_value in vars(args).items():
        if not grabber.config.get(arg_name, None):
            grabber.config[arg_name] = arg_value

    # ensure that the target does not contain a trailing slash
    if grabber.config["target"][-1:] == "/":
        grabber.config["target"] = grabber.config["target"][:-1]

    if grabber.config["target"] not in grabber.config["ignore_duplicates_in"]:
        grabber.config["ignore_duplicates_in"].append(grabber.config["target"])

    # convert to abs path and mkdir
    grabber.config["target"] = os.path.abspath(grabber.config["target"])
    if not os.path.isdir(grabber.config["target"]):
        os.mkdir(grabber.config["target"])

    # Set visited file path
    grabber.visited_file = grabber.config.get("visited_file", None)
    
    # Set queue file path
    grabber.queue_file = grabber.config.get("queue_file", None)
    
    # Load existing visited URLs
    grabber.load_visited_urls()
    
    # Load existing URL queue
    grabber.load_url_queue()

    # Only initialize the queue if it's empty (no saved queue was loaded)
    if not grabber.url_follow_queue:
        grabber.url_follow_queue = deque(grabber.config["url"])
        logging.info("Starting link tree traversal at %s", grabber.url_follow_queue)
    else:
        logging.info("Resuming link tree traversal with %d queued URLs", len(grabber.url_follow_queue))

    print("\nPress ctrl+c to stop.\n")

    # main loop
    urls_processed_since_save = 0
    while grabber.url_follow_queue:
        try:
            logging.info("Queue length: %d URLs remaining", len(grabber.url_follow_queue))
            grabber.visit_next_url()
            urls_processed_since_save += 1
            
            # Save visited URLs and queue periodically
            if grabber.config.get("save_frequency", 100) > 0 and urls_processed_since_save >= grabber.config.get("save_frequency", 100):
                grabber.save_visited_urls()
                grabber.save_url_queue()
                urls_processed_since_save = 0
                
        except requests.exceptions.ConnectionError as connection_error:
            logging.error("Connection error: %s", connection_error)
            
    logging.info("Finished downloading all images successfully!")
    
    # Save visited URLs and queue
    grabber.save_visited_urls()
    grabber.save_url_queue()


# goto main
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped")
        # Save visited URLs and queue on keyboard interrupt
        if 'grabber' in locals():
            grabber.save_visited_urls()
            grabber.save_url_queue()
        exit(0)
