catan-game-recorder
===================

Record games of Settlers of Catan for research purposes, replay purposes, broadcast purposes, etc.

This project also introduces a machine-parsable, human-readable file format for describing a game of Catan.

This is a work in progress.

> Author: Ross Anderson ([rosshamish](https://github.com/rosshamish))

### Usage

```
$ python3 main.py
```

### Demo
![Demo](/doc/gifs/demo.gif)

### File Format

Each `.catan` file contains all publicly known information in the game.
Therefore, each `.catan` file contains sufficient information to 'replay' a game (from a spectator's point of view).

The header begins with a version, and ends with `...CATAN!`. The game begins after that.

Example
```
CatanGameRecord v0.0.1
timestamp: 2015-12-14 23:50:14.603868
players: 4
name: yurick, color: green, seat: 1
name: ross, color: red, seat: 2
name: josh, color: blue, seat: 3
name: zach, color: orange, seat: 4
terrain: wood sheep sheep ore sheep wheat brick wood brick wheat wheat sheep brick ore wood ore desert wood wheat
numbers: 5 6 4 11 3 6 8 8 4 5 9 3 10 10 12 11 None 2 9
ports: 3:1 3:1 sheep2:1 3:1 3:1 ore2:1 brick2:1 wheat2:1 wood2:1
...CATAN!
green rolls 7
red is robbed
green moves robber to 1, steals from blue
green ends turn
blue rolls 2
blue ends turn
orange rolls 2
orange ends turn
red wins
```

See `recording.GameRecord` (in `recording.py`) for all available actions, along with their format.


### Attribution

Originally based off of [fruitnuke/catan](https://github.com/fruitnuke/catan), a catan board generator

### License

GPLv3
