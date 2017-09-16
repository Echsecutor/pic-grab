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
import re
import glob
import json
import os
import sys
import tkinter as tk
from PIL import Image, ImageTk


class Controller(object):

    def __init__(self, root, view, config):
        self.root = root
        self.view = view
        self.config = config
        self.image_list = []
        self.current_image_index = -1

    def __perform_action(self, action):
        """This is a pure man's interpreter for performing actions triggered
        by key events.

        Supported Actions:
        QUIT      exit program
        RELOAD    reload image list from src
        NEXT [n]  go to (n=1)th next image. ( use n < 0 to go back)
        """

        if action == "QUIT":
            self.root.quit()
            return
        if action == "RELOAD":
            self.load_images_from_src()
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

        raise Exception("Unknown action: '{}'".format(action))

    def move_current_image_to(self, target_folder):
        if target_folder[:-1] != "/":
            target_folder += "/"
        cur_img_path = self.image_list[self.current_image_index]
        filename = os.path.basename(cur_img_path)
        target = target_folder + filename
        print("Moving '{}' to '{}'".format(cur_img_path, target))
        os.rename(cur_img_path, target)
        del self.image_list[self.current_image_index]
        self.show_next_img(0)

    def load_images_from_src(self):
        if self.config["src"][:-1] != "/":
            self.config["src"] += "/"

        glob_for = self.config["src"] \
                   + "*" \
                   + self.config["ext"]

        self.image_list = glob.glob(glob_for)
        if not self.image_list:
            raise Exception("No images in '{}'".format(glob_for))
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
        print("Showing img {} '{}'".format(self.current_image_index, new_img_path))

    def handle_key(self, event):

        key_code = event.keycode
        key_char = event.char
        print ('keycode {} (char {})'.format(key_code, key_char))

        if key_code in self.config["key_bindings"].keys():
            self.__perform_action(self.config["key_bindings"][key_code])
        elif key_char in self.config["key_bindings"].keys():
            self.__perform_action(self.config["key_bindings"][key_char])
        else:
            print("No action assigned to key.")
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

    def show_img(self, path):
            im = Image.open(path)
            im.thumbnail((self.root.winfo_width(), self.root.winfo_height()), Image.ANTIALIAS)
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
    config = {}
    if len(sys.argv) > 1:
        cfg_file_path = sys.argv[1]
        if not os.path.isfile(cfg_file_path):
            print("The only allowed command line argument is"
                  + " a config.json file.")
            exit(1)
        with open(cfg_file_path) as cfg_file:
            config = json.load(cfg_file)

    if "src" not in config.keys():
        config["src"] = "./"
    if "key_bindings" not in config.keys():
        config["key_bindings"] = {}
    if "ext" not in config.keys():
        config["ext"] = ".jpg"

    for key, val in config["key_bindings"].copy().items():
        try:
            # convert integer keys to int
            print("trying to cenvert {} -> {}".format(key, val))
            config["key_bindings"][int(key)] = val
            print("converted")
        except:
            pass

    # key_code 9 = esc -> quit
    config["key_bindings"][9] = "QUIT"

    if "r" not in config["key_bindings"].keys():
        config["key_bindings"]["r"] = "RELOAD"

    return config


def main():

    config = init_config()

    # init tk view/control
    root = tk.Tk()
    view = ImgView(root)
    ctrl = Controller(root, view, config)
    view.register_key_listener(lambda e: ctrl.handle_key(e))
    ctrl.load_images_from_src()

    root.mainloop()


# goto main
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped")
        exit(0)
