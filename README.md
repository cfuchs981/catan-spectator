catan-spectator
---------------

Transcribe games of Settlers of Catan for research purposes, replay purposes, broadcast purposes, etc.

This project introduces a machine-parsable, human-readable file format for describing a game of Catan.

This is a work in progress.

> Author: Ross Anderson ([rosshamish](https://github.com/rosshamish))

### Usage

```
$ python3 main.py --help
usage: main.py [-h] [--terrain TERRAIN] [--numbers NUMBERS] [--ports PORTS]
               [--pieces PIECES] [--players PLAYERS] [--pregame PREGAME]

log a game of catan

optional arguments:
  -h, --help         show this help message and exit
  --terrain TERRAIN  random|preset|empty|debug, default empty
  --numbers NUMBERS  random|preset|empty|debug, default empty
  --ports PORTS      random|preset|empty|debug, default preset
  --pieces PIECES    random|preset|empty|debug, default empty
  --players PLAYERS  random|preset|empty|debug, default preset
  --pregame PREGAME  on|off, default on
```

Make targets:
- `make relaunch`: launch (or relaunch) the GUI
- `make logs`: cat the python logs
- `make tail`: tail the python logs
- `make`: alias for relaunch && tail

### Demo
![Demo](/doc/gifs/demo3.gif)

### File Format

Each `.catan` file contains all publicly known information in the game.
Therefore, each `.catan` file contains sufficient information to 'replay' a game (from a spectator's point of view).

The header begins with a version, and ends with `...CATAN!`. The game begins after that.

The format is not yet v1.0. The current version is listed in `catanlog.py`.

Example
```
catanlog v0.2.0
timestamp: 2015-12-27 15:19:57.723284
players: 4
name: yurick, color: green, seat: 1
name: josh, color: blue, seat: 2
name: zach, color: orange, seat: 3
name: ross, color: yellow, seat: 4
terrain: wood wood brick sheep ore sheep wheat brick wood ore sheep wood sheep ore wheat wheat desert wheat brick
numbers: 3 6 8 10 2 11 12 9 8 10 5 6 9 4 3 11 None 5 4
ports: 3:1 ore2:1 3:1 sheep2:1 3:1 wood2:1 brick2:1 3:1 wheat2:1
...CATAN!
green rolls 4
green buys road, builds at 154
green buys settlement, builds at 171
green buys settlement, builds at 188
green ends turn
blue rolls 4
blue buys city, builds at 154
blue buys dev card
blue buys dev card
blue plays dev card: knight on None, steals from color
blue plays dev card: victory point
blue ends turn
orange rolls 4
orange ends turn
yellow wins
```

See `catanlog.CatanLog` (in `catanlog.py`) for all available actions, along with their format.

### Todo

Core
- [x] robber move, steal from player (account for steal from nobody case)
- [x] trading with people
- [x] trading with port
- [x] knight -> robber move, steal from player
- [ ] ports configurable
- [ ] fix victory point doesn't work first click each turn

Nice to have
- [ ] cancelling of roads/settlements/cities while placing
- [ ] save log file to custom location on End Game
- [ ] images, colors in UI buttons (eg dice for roll, )
- [ ] city-shaped polygon for cities
- [ ] tile images instead of colored hexagons
- [ ] port images instead of colored triangles
- [ ] piece images instead of colored polygons
- [ ] number images instead of text

### Attribution

Codebase originally forked from [fruitnuke/catan](https://github.com/fruitnuke/catan), a catan board generator

Hexagonal grid system based off of [jdmonin/JSettlers2](https://github.com/jdmonin/JSettlers2), a catan implementation used for research

### License

GPLv3
