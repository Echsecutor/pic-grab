#!/usr/bin/python3
"""This is a small command line utility to grab pictures from a web
gui to view them locally. Which links to follow and what to download
can be configured using regular expressions.

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

import requests
import re
from getpass import getpass
import logging
import json
import sys

from collections import deque

url_follow_queue = deque()
"pool of urls to visit next"

visited_urls = set()
"do not visit those again"

session = requests.Session()

config = {}
"Holds the configuration, typically loaded from a json file."


def filename_from_url(url):
    match = re.search("[^/]+$", url)
    if match:
        return match.group()
    return None


def process_found_url(url):
    if url in visited_urls:
        return
    visited_urls.add(url)

    for reg in config["follow"]:
        if re.match(reg, url):
            url_follow_queue.append(url)

    for reg in config["download"]:
        if re.match(reg, url):
            result = session.get(url)
            filename = filename_from_url(result.url)
            if not filename:
                logging.error("Can not determine filename from %s", result.url)
                return
            with open(config["target"] + filename, 'w') as out_file:
                out_file.write(result.content)


def visit_next_url():
    url = url_follow_queue.popleft()
    r = session.get(url)

    # find more urls
    for m in re.finditer(r"""(https?://[^\s<>]+)|href=['"]([^"']+)""", r.text):
        for g in m.groups():
            if g:
                process_found_url(g)


def main():
    """The main function gets a list of all mailing lists on the given
    server and performs (an) action(s) on all lists.

    """
    import argparse

    logger_cfg = {
        "level":
        logging.INFO,
        "format":
        "%(asctime)s %(funcName)s (%(lineno)d) [%(levelname)s]:    %(message)s"
    }

    parser = argparse.ArgumentParser(
        description="Perform some action on all lists " +
        "at a given mailman site.",
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
        "-t",
        "--target",
        help="The directory to hold the resulting files.",
        default="fetched/")

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

    logger_cfg["level"] = getattr(logging, args.log)
    logging.basicConfig(**logger_cfg)

    print("Log messages above level: {}".format(logger_cfg["level"]))

    if args.config:
        with open(args.config, "r") as cfg_file:
            config = json.load(cfg_file)

    if args.url:
        config["url"] = args.url

    if not config.get("url", None):
        logging.critical("No base url(s) given.")
        parser.print_help()
        sys.exit(1)
    else:
        logging.info("url: '%s'", config["url"])

    if not config.get("download", None):
        config["download"] = args.download

    if not config.get("follow", None):
        config["follow"] = args.follow

    url_follow_queue = deque(config["url"])
    logging.info("Starting link tree traversal at %s", url_follow_queue)
    while url_follow_queue:
        visit_next_url()


# goto main
if __name__ == "__main__":
    main()
