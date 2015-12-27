import datetime
import os
import sys
import collections

Version = collections.namedtuple('Version', ['major', 'minor', 'patch'])

class CatanLog(object):
    """
    class CatanLog introduces a machine-parsable, human-readable log of all actions made in a game of Catan.

    Each log contains all publicly known information in the game.
    Each log is sufficient to 'replay' a game.

    Use #dump to get the log as a string.
    Use #flush to write the log to a file.

    TODO log private information as well (which dev card picked up, which card stolen)
    """
    version = Version(major=0, minor=2, patch=0)

    def __init__(self, auto_flush=True, log_dir='log', use_stdout=False):
        self._log = str()

        self._chars_flushed = 0
        self._auto_flush = auto_flush
        self._log_dir = log_dir
        self._use_stdout = use_stdout

        self.timestamp = datetime.datetime.now()
        self.players = list()

    def log(self, content):
        """
        Writes a string to the log
        """
        self._log += content
        if self._auto_flush:
            self.flush(self._log_dir, self._use_stdout)

    def logln(self, content):
        """Writes a string to the log, appending a newline
        """
        self.log('{0}\n'.format(content))

    def dump(self):
        """Dumps the entire log to a string, and returns it
        """
        return self._log

    def _latest(self):
        """Gets all characters written to _log since the last flush()
        """
        return self._log[self._chars_flushed:]

    def filename(self, log_dir):
        """Returns a unique string based on the timestamp and players involved
        """
        name = '{}-{}.catan'.format(self.timestamp.isoformat(), '-'.join([p.name for p in self.players]))
        path = os.path.join(log_dir, name)
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        return path

    def flush(self, log_dir, use_stdout):
        """Appends the latest updates to file, or optionally to stdout instead
        """
        latest = self._latest()
        self._chars_flushed += len(latest)
        if use_stdout:
            file = sys.stdout
        else:
            file = open(self.filename(log_dir), 'a')

        print(latest, file=file, flush=True, end='')

        if not use_stdout:
            file.close()

    def log_initial_game_info(self, players, terrain, numbers, ports):
        """
        Begins a game by logging
        - file format version
        - timestamp
        - players
        - board layout

        :param players: set of 3 or (ideally) 4 #Players
        :param terrain: list of 19 terrain types as defined in #models (eg resource.WOOD)
        :param numbers: list of 19 numbers, 1 each of (2,12), 2 each of all others
        :param ports: list of 9 ports as defined in #models (eg port.THREE_FOR_ONE)
        """
        self._set_players(players)
        self.logln('catanlog v{}.{}.{}'.format(CatanLog.version.major,
                                               CatanLog.version.minor,
                                               CatanLog.version.patch))
        self.logln('timestamp: {0}'.format(self.timestamp))
        self._log_players(players)
        self._log_board_terrain(terrain)
        self._log_board_numbers(numbers)
        self._log_board_ports(ports)
        self.logln('...CATAN!')

    def log_player_roll(self, player, roll):
        """
        $color rolls $number
        """
        self.logln('{0} rolls {1}'.format(player.color, roll))

    def log_player_is_robbed(self, player):
        """
        $color is robbed
        """
        self.logln('{0} is robbed'.format(player.color))

    def log_player_moves_robber_and_steals(self, player, tile_id, victim):
        """
        $color moves robber to $hex, steals from $color
        """
        self.logln('{0} moves robber to {1}, steals from {2}'.format(
            player.color,
            tile_id,
            victim.color
        ))

    def log_player_buys_settlement(self, player, node_id):
        """
        $color buys settlement, builds at $location
        """
        self.logln('{0} buys settlement, builds at {1}'.format(
            player.color,
            node_id
        ))

    def log_player_buys_city(self, player, node_id):
        """
        $color buys city, builds at $location
        """
        self.logln('{0} buys city, builds at {1}'.format(
            player.color,
            node_id
        ))

    def log_player_buys_dev_card(self, player):
        """
        $color buys dev card
        """
        self.logln('{0} buys dev card'.format(
            player.color
        ))

    def log_player_buys_road(self, player, edge):
        """
        $color buys road, builds at $location
        """
        self.logln('{0} buys road, builds at {1}'.format(
            player.color,
            edge
        ))

    def log_player_trades_with_port(self, player, to_port, port, to_player):
        """
        $color trades $number $resources[, $number resources]* to port:$port for $number $resources[, $number resources]*

        the to_resources params are dicts of form {'wood':2,'brick':1}
        """
        self.log('{0} trades '.format(player.color))

        # to_other items
        self.log('[')
        for i, (res, num) in enumerate(to_port.items()):
            if i > 0:
                self.log(',')
            self.log('{0} {1}'.format(num, res.value))
        self.log(']')

        self.log(' to port:{0} for '.format(port))

        # to_player items
        self.log('[')
        for i, (res, num) in enumerate(to_player.items()):
            if i > 0:
                self.log(',')
            self.log('{0} {1}'.format(num, res.value))
        self.log(']')

        self.log('\n')

    def log_player_trades_with_other(self, player, to_other, other, to_player):
        """
        $color trades [$number $resources, $number resources] to player:$color for [$number $resources, $number resources]

        the to_resources params are dicts of form {'wood':2,'brick':1}
        """
        self.log('{0} trades '.format(player.color))

        # to_other items
        self.log('[')
        for i, (res, num) in enumerate(to_other.items()):
            if i > 0:
                self.log(',')
            self.log('{0} {1}'.format(num, res.value))
        self.log(']')

        self.log(' to player:{0} for '.format(other.color))

        # to_player items
        self.log('[')
        for i, (res, num) in enumerate(to_player.items()):
            if i > 0:
                self.log(',')
            self.log('{0} {1}'.format(num, res.value))
        self.log(']')

        self.log('\n')

    def log_player_plays_dev_knight(self, player, tile_id, victim):
        """
        $color plays dev card: knight on $hex, steals from $color
        """
        self.logln('{0} plays dev card: knight on {1}, steals from {2}'.format(
            player.color,
            tile_id,
            victim.color
        ))

    def log_player_plays_dev_monopoly(self, player, resource):
        """
        $color plays dev card: monopoly on $resource

        resource is the lowercase fulltext, eg 'wood', 'wheat', 'brick', 'ore', 'sheep'
        """
        self.logln('{0} plays dev card: monopoly on {1}'.format(
            player.color,
            resource.value
        ))

    def log_player_plays_dev_victory_point(self, player):
        """
        $color plays dev card: victory point
        """
        self.logln('{0} plays dev card: victory point'.format(player.color))

    def log_player_plays_dev_road_builder(self, player, edge1, edge2):
        """
        $color plays dev card: road builder, builds at $location and $location
        """
        self.logln('{0} plays dev card: road builder, builds at {1} and {2}'.format(
            player.color,
            edge1,
            edge2
        ))

    def log_player_ends_turn(self, player):
        """
        $color ends turn
        """
        self.logln('{0} ends turn'.format(player.color))

    def log_player_wins(self, player):
        self.logln('{0} wins'.format(player.color))

    def _log_board_terrain(self, terrain):
        self.logln('terrain: {0}'.format(' '.join(t.value for t in terrain)))

    def _log_board_numbers(self, numbers):
        self.logln('numbers: {0}'.format(' '.join(str(n.value) for n in numbers)))

    def _log_board_ports(self, ports):
        self.logln('ports: {0}'.format(' '.join(p.value for p in ports)))

    def _log_players(self, players):
        self.logln('players: {0}'.format(len(players)))
        for p in self.players:
            self.logln('name: {0}, color: {1}, seat: {2}'.format(p.name, p.color, p.seat))

    def _set_players(self, _players):
        self.players = list()
        _players = list(_players)
        _players.sort(key=lambda p: p.seat)
        for p in _players:
            self.players.append(p)
