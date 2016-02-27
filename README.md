catan-spectator
---------------

Transcribe games of Settlers of Catan for research purposes, replay purposes, broadcast purposes, etc.

The UI is feature-complete, and can be used to log games.

Related packages:
* [`catan`](https://github.com/rosshamish/catan-py)
* [`catanlog`](https://github.com/rosshamish/catanlog)
* [`hexgrid`](https://github.com/rosshamish/hexgrid)
* [`undoredo`](https://github.com/rosshamish/undoredo)

Todos are listed below.

> Author: Ross Anderson ([rosshamish](https://github.com/rosshamish))

### Demo
![Demo](/doc/gifs/demo4.gif)

### Installation

If you don't have brew, go to http://brew.sh and install it.

If you don't have python3, do `$ brew install python3`

```
$ pip3 install catan-spectator
```

### Usage

Basic usage:
```
$ catan-spectator
```

For a particular board layout:
```
$ catan-spectator --board 'o s w w o s s h b h w s w h h b o d b 5 2 8 10 9 8 5 3 4 6 3 6 10 12 11 9 11 None 4'
```

Terrain are referred to by their first letter in lowercase, except wheat, which is an h.
Numbers are referred to by their corresponding digit, and "None" represents no number. Exactly nineteen terrain
characters are expected, and exactly nineteen numbers are expected.

| Terrain Name | Short Code |
| --- | --- |
| Wood | w |
| Brick | b |
| Wheat | h |
| Sheep | s |
| Ore | o |
| Desert | d |

For a full list of options:
```
$ catan-spectator --help
```

### Hotkeys

| Key | Action |
| ---| ------ |
| 2 | roll 2 |
| 3 | roll 3 |
| 4 | roll 4 |
| 5 | roll 5 |
| 6 | roll 6 |
| 7 | roll 7 |
| 8 | roll 8 |
| 9 | roll 9 |
| 0 | roll 10 |
| - | roll 11 |
| = | roll 12 |
| r | buy road |
| s | buy settlement |
| c | buy city |
| d | buy dev card |
| k | play knight |
| left arrow | undo |
| right arrow | redo |
| space bar | end turn |

### File Format

<!-- remember to update this section in sync with "File Format" in github.com/rosshamish/catan-py/README.md -->

catan-spectator writes game logs in the `.catan` format described by package [`catanlog`](https://github.com/rosshamish/catanlog).

They look like this:

```
green rolls 6
blue buys settlement, builds at (1 NW)
orange buys city, builds at (1 SE)
red plays monopoly on ore
```

### Development

```
$ git clone https://github.com/rosshamish/catan-spectator
$ cd catan-spectator
$ pip3 install -r requirements.txt
```

```
$ python3 main.py
```

Make targets:
- `make relaunch`: launch (or relaunch) the GUI
- `make logs`: cat the python logs
- `make tail`: tail the python logs
- `make`: alias for relaunch && tail

##### Todo

Need to have
- [ ] views documented
- [x] piece placing should be cancellable (via undo)
- [x] all actions should be undoable
- [ ] ui+catanlog: save log file to custom location on End Game
- [ ] ui: city-shaped polygon for cities
- [ ] ui/ux improvements

Nice to have
- [ ] board: random number setup obeys red number rule
- [ ] ui+board+hexgrid: during piece placement, use little red x’s (at least in debug mode) on “killed spots”
- [ ] ui+game+player+states: dev cards, i.e. keep a count of how many dev cards a player has played and enable Play Dev Card buttons if num > 0
- [x] ui+game+port+hexgrid: port trading, disable buttons if the current player doesn’t have the port. 4:1 is always enabled.
- [x] ui+port+hexgrid: port trading, don't allow getting or giving more or less than defined by the port type (3:1, 2:1).
- [ ] ui+port: port trading, don’t allow n for 0 trades
- [ ] ui: large indicator off what the current player is (and what the order is)
- [x] ui: cancelling of roads/settlements/cities while placing
- [ ] ui: images, colors in UI buttons (eg dice for roll, )
- [attempted, might be worse] ui: tile images instead of colored hexagons
- [ ] ui: port images instead of colored triangles
- [ ] ui: piece images instead of colored polygons
- [x] ui: number images instead of text (or avoid contrast issues otherwise)
- [ ] ui+game+states+robber: steal dropdown has “nil” option always, for in case it goes on a person with no cards and no steal happens. Name it something obvious, don’t use an empty string.

### Attribution

Codebase originally forked from [fruitnuke/catan](https://github.com/fruitnuke/catan), a catan board generator

### License

GPLv3
