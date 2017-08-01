"""Display pictures from a folder and sort them into other folders by
pressing keys. The config file needs to specify the source dir and a
dict with { key_1: target_dir_1, key_2: target_dir_2, ...}.

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

import tkinter as tk
from PIL import Image, ImageTk


class Controller(object):

    def __init__(self, root, view):
        self.root = root
        self.view = view

    def handle_key(self, event):

        keycode = event.keycode
        print ('keycode {} (char {})'.format(keycode, event.char))
        if keycode == 9:
            # esc -> quit
            self.root.quit()

        # TODO: handdle sort keys

        # TODO: get next img path
        self.view.show_img('ham/ff9a4cc32c13d2608b24dc58e2a05df5.jpg')


class ImgView(object):

    def __init__(self, root):
        self.frame = tk.Frame(root)
        self.frame.pack()
        self.frame.focus_set()

        self.label = tk.Label(self.frame)
        self.label.pack()

        self.image_path = ""

    def show_img(self, path):
            im = Image.open(path)
            tkimage = ImageTk.PhotoImage(im)
            self.label.configure(image=tkimage)
            self.label.image = tkimage
            self.image_path = path

    def register_key_listener(self, key_listener):
        self.frame.bind("<Key>", key_listener)


def main():
    root = tk.Tk()
    view = ImgView(root)
    ctrl = Controller(root, view)
    view.register_key_listener(lambda e: ctrl.handle_key(e))
    root.mainloop()


# goto main
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped")
        exit(0)
