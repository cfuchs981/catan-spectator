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
![Demo](/doc/gifs/demo4.gif)

### File Format

Each `.catan` file contains all publicly known information in the game.
Therefore, each `.catan` file contains sufficient information to 'replay' a game (from a spectator's point of view).

The header begins with a version, and ends with `...CATAN!`. The game begins after that.

Locations are integer values of hexagonal coordinates as defined in module hexgrid (`hexgrid.py`).

The format is not yet v1.0. The current version is listed in `catanlog.py`.

Example
```
catanlog v0.4.3
timestamp: 2015-12-30 03:21:56.572418
players: 4
name: yurick, color: green, seat: 1
name: josh, color: blue, seat: 2
name: zach, color: orange, seat: 3
name: ross, color: red, seat: 4
terrain: desert brick sheep brick ore brick wheat wood wood wheat wood sheep ore wood sheep sheep wheat ore wheat
numbers: None 4 6 9 8 10 5 8 10 5 3 11 3 9 12 11 6 4 2
ports: 3:1(1 NW) ore(2 W) 3:1(4 W) sheep(5 SW) 3:1(6 SE) wood(8 SE) brick(9 E) 3:1(10 NE) wheat(12 NE)
...CATAN!
green buys settlement, builds at (17 NW)
green buys road, builds at (17 NW)
green ends turn
blue buys settlement, builds at (8 NW)
blue buys road, builds at (8 NW)
blue ends turn
orange buys settlement, builds at (3 SE)
orange buys road, builds at (3 SE)
orange ends turn
red buys settlement, builds at (5 NE)
red buys road, builds at (5 E)
red ends turn
red buys settlement, builds at (13 S)
red buys road, builds at (13 SE)
red ends turn
orange buys settlement, builds at (10 NW)
orange buys road, builds at (11 SW)
orange ends turn
blue buys settlement, builds at (9 NW)
blue buys road, builds at (9 NW)
blue ends turn
green buys settlement, builds at (2 SW)
green buys road, builds at (2 W)
green ends turn
green rolls 4
green buys road, builds at (2 NW)
green ends turn
blue rolls 6
blue plays dev card: road builder, builds at (9 W) and (10 E)
blue buys settlement, builds at (10 NE)
blue trades [1 wheat, 1 brick] to player green for [1 sheep]
```

See `catanlog.CatanLog` (in `catanlog.py`) for all available actions, along with their format.

### Todo

Core
- [x] robber move, steal from player (account for steal from nobody case)
- [x] trading with people
- [x] trading with port
- [x] knight -> robber move, steal from player
- [x] ports configurable
- [x] fix victory points do not work first click each turn
- [x] robber movable during game setup
- [ ] implement year of plenty dev card
- [ ] catanlog: if a 2 is rolled, syntax is “$color rolls 2 …DEUCES!”
- [x] modules documented
- [ ] views documented

Nice to have
- [ ] board: random number setup obeys red number rule
- [ ] ui+board+hexgrid: during piece placement, use little red x’s (at least in debug mode) on “killed spots”
- [ ] ui+game+player+states: dev cards, i.e. keep a count of how many dev cards a player has played and enable Play Dev Card buttons if num > 0
- [ ] ui+game+port+hexgrid: port trading, buttons are disabled if the current player doesn’t have the port. 4:1 is always enabled.
- [ ] ui+port+hexgrid: port trading, can’t get or give more or less than defined by the port type (3:1, 2:1).
- [ ] ui+port: port trading, don’t allow n for 0 trades
- [ ] ui: large indicator off what the current player is (and what the order is)
- [ ] ui: cancelling of roads/settlements/cities while placing
- [ ] ui+catanlog: save log file to custom location on End Game
- [ ] ui: images, colors in UI buttons (eg dice for roll, )
- [ ] ui: city-shaped polygon for cities
- [ ] ui: tile images instead of colored hexagons
- [ ] ui: port images instead of colored triangles
- [ ] ui: piece images instead of colored polygons
- [ ] ui: number images instead of text (or avoid contrast issues otherwise)
- [ ] ui: roll frame: up on 12 goes to 2
- [ ] ui+game+states+steal: steal dropdown has “nil” option always, for in case it goes on a person with no cards and no steal happens. Name it something obvious, don’t use an empty string.

### Attribution

Codebase originally forked from [fruitnuke/catan](https://github.com/fruitnuke/catan), a catan board generator

Hexagonal grid system based off of [jdmonin/JSettlers2](https://github.com/jdmonin/JSettlers2), a catan implementation used for research

### License

GPLv3
