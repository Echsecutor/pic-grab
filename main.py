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
                    logging.error("Error fetching file %s.", url)
                    return

                with open(output_path, 'wb') as output_file:
                    output_file.write(response.content)

    def visit_next_url(self):
        """
        Pop the next url, retrieve it and scan the content for further links.
        """

        url = self.url_follow_queue.popleft()
        response = self.session.get(url)

        # find more urls
        for match in re.finditer(
                r"""(https?://[^\s<>]+)|href=['"]([^"']+)|src=['"]([^"']+)""",
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


def main():
    """The main function gets a list of all mailing lists on the given
    server and performs (an) action(s) on all lists.

    """
    import argparse

    logger_config = {
        "level":
        logging.INFO,
        "format":
        "%(asctime)s %(funcName)s (%(lineno)d) [%(levelname)s]:    %(message)s"
    }

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

    args = parser.parse_args()

    logger_config["level"] = getattr(logging, args.log)
    logging.basicConfig(**logger_config)

    print("Log messages above level: {}".format(logger_config["level"]))

    grabber = Grabber()

    if args.config:
        with open(args.config, "r") as config_file:
            grabber.config = json.load(config_file)

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

    grabber.url_follow_queue = deque(grabber.config["url"])
    logging.info("Starting link tree traversal at %s",
                 grabber.url_follow_queue)

    print("\nPress ctrl+c to stop.\n")

    # main loop
    while grabber.url_follow_queue:
        try:
            logging.info("Queue length: %d URLs remaining", len(grabber.url_follow_queue))
            grabber.visit_next_url()
        except requests.exceptions.ConnectionError as connection_error:
            logging.error("Connection error: %s", connection_error)
            
    logging.info("Finished downloading all images successfully!")


# goto main
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped")
        exit(0)
