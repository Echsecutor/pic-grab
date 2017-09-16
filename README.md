# pic-grab
Got bored from training your neural networks on recognising cats?
With these small python scripts you can quickly gather a sample of pictures and then manually sort them into categories.

## Grabber
To gether a sample of pictures from some website, run the pic grabber like
```
python3 main.py -h
```
for a usage help. It is recommended to use a config file like so
```
python3 main.py -c grabber.cfg.json
```
see the grabber.cfg.json for an example.

Make sure to gather only from sites which allow automated gathering and only such pictures which are free.


## Sorter
After you got some pictures, you may sort them using
```
python3 sorter.py sorter.cfg.json
```
See the example config file for sensible options and key bindings. The esc key will always get you out of the sorter. ;)




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
