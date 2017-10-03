"""Display pictures from a folder and sort them into other folders by
pressing keys.

.. module:: sorter

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
import exifread
import glob
import json
import logging
import os
from PIL import Image, ImageTk
import re
from shutil import copyfile
import tkinter as tk


class Controller(object):

    def __init__(self, root, view, key_bindings, image_files):
        self.root = root
        self.view = view
        self.key_bindings = key_bindings
        self.image_files = image_files
        self.image_list = []
        self.current_image_index = -1

    def __perform_action(self, action):
        """This is a pure man's interpreter for performing actions triggered
        by key events.

        Supported Actions:
        QUIT       exit program
        RELOAD     reload image list from src
        NEXT [n]   go to (n=1)th next image. ( use n < 0 to go back)
        MOVE [TO]  mv pic to folder TO
        COPY [TO]  cp pic to folde TO
        DEL        delete pic
        """

        if action == "QUIT":
            logging.critical("Goodbye!")
            self.root.quit()
            return
        if action == "RELOAD":
            self.load_images_from_src()
            return
        if action == "DEL":
            self.delete_current_image()
            return

        match = re.match(r"NEXT\s*(-?[0-9]+)?", action)
        if match:
            n = 1
            if match.group(1):
                n = int(match.group(1))
            self.show_next_img(n)
            return

        match = re.match(r"MOVE\s*([^\s].*)", action)
        if match:
            self.move_current_image_to(match.group(1))
            return

        match = re.match(r"COPY\s*([^\s].*)", action)
        if match:
            self.copy_current_image_to(match.group(1))
            return


        raise Exception("Unknown action: '{}'".format(action))

    def delete_current_image(self):
        cur_img_path = self.image_list[self.current_image_index]
        del self.image_list[self.current_image_index]
        os.remove(cur_img_path)
        logging.info("'{}' deleted".format(cur_img_path))
        self.show_next_img(0)

    def get_target_file_name(self, target_folder):
        if target_folder[:-1] != "/":
            target_folder += "/"
        cur_img_path = self.image_list[self.current_image_index]
        filename = os.path.basename(cur_img_path)
        target = target_folder + filename
        logging.info("'{}' to '{}'".format(cur_img_path, target))
        return cur_img_path, target

    def move_current_image_to(self, target_folder):
        logging.info("Moving", end=" ")
        cur_img_path, target = self.get_target_file_name(target_folder)
        os.rename(cur_img_path, target)
        del self.image_list[self.current_image_index]
        self.show_next_img(0)

    def copy_current_image_to(self, target_folder):
        logging.info("Copying", end=" ")
        cur_img_path, target = self.get_target_file_name(target_folder)
        copyfile(cur_img_path, target)
        self.show_next_img(0)

    def load_images_from_src(self):
        if isinstance(self.image_files, str):
            self.image_files = [self.image_files, ]
        for glob_for in self.image_files:
            self.image_list += glob.glob(glob_for)

        if not self.image_list:
            raise Exception("No images found in '{}'".format(self.image_files))
        self.image_list.sort()
        self.current_image_index = 0

    def show_next_img(self, index_change=1):
        if not self.image_list:
            self.load_images_from_src()
        self.current_image_index += index_change
        while self.current_image_index < 0:
            self.current_image_index += len(self.image_list)
        self.current_image_index %= len(self.image_list)

        new_img_path = self.image_list[self.current_image_index]
        self.view.show_img(new_img_path)
        logging.info("Showing img {} '{}'".format(self.current_image_index, new_img_path))

    def handle_key(self, event):

        key_code = event.keycode
        key_char = event.char
        logging.debug('keycode {} (char {})'.format(key_code, key_char))

        if key_code in self.key_bindings.keys():
            self.__perform_action(self.key_bindings[key_code])
        elif key_char in self.key_bindings.keys():
            self.__perform_action(self.key_bindings[key_char])
        else:
            logging.warning("No action assigned to key.")
            # TODO: ask user -> assign action


class ImgView(object):

    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()
        self.frame.focus_set()

        self.label = tk.Label(self.frame)
        self.label.pack()

        self.image_path = ""

    def _read_img_and_correct_exif_orientation(path):
        im = Image.open(path)
        tags = {}
        with open(path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
        if "Image Orientation" in tags.keys():
            orientation = tags["Image Orientation"]
            logging.debug("Orientation: %s (%s)", orientation, orientation.values)
            val = orientation.values
            if 5 in val:
                val += [4,8]
            if 7 in val:
                val += [4, 6]
            if 3 in val:
                logging.debug("Rotating by 180 degrees.")
                im = im.transpose(Image.ROTATE_180)
            if 4 in val:
                logging.debug("Mirroring horizontally.")
                im = im.transpose(Image.FLIP_TOP_BOTTOM)
            if 6 in val:
                logging.debug("Rotating by 270 degrees.")
                im = im.transpose(Image.ROTATE_270)
            if 8 in val:
                logging.debug("Rotating by 90 degrees.")
                im = im.transpose(Image.ROTATE_90)

        return im

    def show_img(self, path):
        im = ImgView._read_img_and_correct_exif_orientation(path)
        im.thumbnail((self.root.winfo_width(),
                      self.root.winfo_height()), Image.ANTIALIAS)
        tkimage = ImageTk.PhotoImage(im)
        self.label.configure(image=tkimage)
        self.label.image = tkimage
        self.image_path = path

    def register_key_listener(self, key_listener):
        self.frame.bind("<Key>", key_listener)


def init_config():
    """Load config. json if file given on command line. Set defaults, if
    not given. Return config dictionary.

    """
    import argparse
    parser = argparse.ArgumentParser(
        description="Image viewer with configurable key bindings"
        + " for the elementary operations (move/delete).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-c",
        "--config",
        help="Read config with keybindings from JSON file.",
        default="sorter.cfg.json")

    parser.add_argument(
        "image_files",
        nargs="*",
        help="Glob or List of image files to work on.",
        default="*.jpg")

    args = parser.parse_args()

    key_bindings = {}
    cfg_file_path = args.config
    if not os.path.isfile(cfg_file_path):
        logging.critical("Config file not found.")
        exit(1)
    with open(cfg_file_path) as cfg_file:
        key_bindings = json.load(cfg_file)

    for key, val in key_bindings.copy().items():
        try:
            # convert integer keys to int
            logging.debug("trying to convert {} -> {}".format(key, val))
            key_bindings[int(key)] = val
            logging.debug("converted")
        except:
            pass

    # key_code 9 = esc -> quit
    key_bindings[9] = "QUIT"

    if "r" not in key_bindings.keys():
        key_bindings["r"] = "RELOAD"

    return key_bindings, args.image_files


def main():

    logging.basicConfig(level=logging.DEBUG)

    key_bindings, image_files = init_config()

    # init tk view/control
    root = tk.Tk()
    view = ImgView(root)
    ctrl = Controller(root, view, key_bindings, image_files)
    view.register_key_listener(lambda e: ctrl.handle_key(e))
    ctrl.load_images_from_src()

    root.mainloop()


# goto main
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("\n\nStopped")
        exit(0)
