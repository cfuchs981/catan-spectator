import datetime
import sys


class GameRecord(object):
    """
    class GameRecord introduces a machine-parsable, human-readable record of all actions made in a game of Catan.

    Each record contains all publicly known information in the game.
    Each record is sufficient to 'replay' a game.

    Use #dump to get the record as a string.
    Use #flush to write the record to a file.

    TODO record private information as well (which dev card picked up, which card stolen)
    """
    version = '0.0.2'

    def __init__(self, auto_flush=True, use_stdout=True):
        self._record_str = str()

        self._chars_flushed = 0
        self._auto_flush = auto_flush
        self._use_stdout = use_stdout

        self.timestamp = datetime.datetime.now()
        self.player_names = list()

    def record(self, content):
        """
        Writes a string to the record
        """
        self._record_str += content
        if self._auto_flush:
            self.flush(use_stdout=self._use_stdout)

    def recordln(self, content):
        """Writes a string to the record, appending a newline
        """
        self.record('{0}\n'.format(content))

    def dump(self):
        """Dumps the entire record to a string, and returns it
        """
        return self._record_str

    def _latest(self):
        """Gets all characters written to _record_str since the last flush()
        """
        return self._record_str[self._chars_flushed:]

    def filename(self):
        """Returns a unique string based on the timestamp and players involved
        """
        return '{}-{}.catan'.format(self.timestamp.isoformat(), '-'.join(self.player_names))

    def flush(self, use_stdout=False):
        """Appends the latest updates to file, or optionally to stdout instead
        """
        latest = self._latest()
        self._chars_flushed += len(latest)
        if use_stdout:
            file = sys.stdout
        else:
            file = open(self.filename(), 'a')

        print(latest, file=file, flush=True, end='')

        if not use_stdout:
            file.close()

    def record_initial_game_info(self, players, terrain, numbers, ports):
        """
        Begins a game by recording
        - file format version
        - timestamp
        - players
        - board layout

        :param players: set of 3 or (ideally) 4 #Players
        :param terrain: list of 19 terrain types as defined in #models (eg resource.WOOD)
        :param numbers: list of 19 numbers, 1 each of (2,12), 2 each of all others
        :param ports: list of 9 ports as defined in #models (eg port.THREE_FOR_ONE)
        """
        self.recordln('CatanGameRecord v{0}'.format(GameRecord.version))
        self.recordln('timestamp: {0}'.format(self.timestamp))
        self._record_players(players)
        self._record_board_terrain(terrain)
        self._record_board_numbers(numbers)
        self._record_board_ports(ports)
        self.recordln('...CATAN!')

    def record_player_roll(self, player, roll):
        """
        $color rolls $number
        """
        self.recordln('{0} rolls {1}'.format(player.color, roll))

    def record_player_is_robbed(self, player):
        """
        $color is robbed
        """
        self.recordln('{0} is robbed'.format(player.color))

    def record_player_moves_robber_and_steals(self, player, tile_id, victim):
        """
        $color moves robber to $hex, steals from $color
        """
        self.recordln('{0} moves robber to {1}, steals from {2}'.format(
            player.color,
            tile_id,
            victim.color
        ))

    def record_player_buys_settlement(self, player, node_id):
        """
        $color buys settlement, builds at $location
        """
        self.recordln('{0} buys settlement, builds at {1}'.format(
            player.color,
            node_id
        ))

    def record_player_buys_city(self, player, node_id):
        """
        $color buys city, builds at $location
        """
        self.recordln('{0} buys city, builds at {1}'.format(
            player.color,
            node_id
        ))

    def record_player_buys_dev_card(self, player):
        """
        $color buys dev card
        """
        self.recordln('{0} buys dev card'.format(
            player.color
        ))

    def record_player_buys_road(self, player, edge):
        """
        $color buys road, builds at $location
        """
        self.recordln('{0} buys road, builds at {1}'.format(
            player.color,
            edge
        ))

    def record_player_trades_with_port(self, player, to_port, port, to_player):
        """
        $color trades $number $resources[, $number resources]* to port:$port for $number $resources[, $number resources]*

        the to_resources params are dicts of form {'wood':2,'brick':1}
        """
        self.record('{0} trades '.format(player.color))

        # to_other items
        self.record('[')
        for i, (res, num) in enumerate(to_port.items()):
            if i > 0:
                self.record(',')
            self.record('{0} {1}'.format(num, res.value))
        self.record(']')

        self.record(' to port:{0} for '.format(port))

        # to_player items
        self.record('[')
        for i, (res, num) in enumerate(to_player.items()):
            if i > 0:
                self.record(',')
            self.record('{0} {1}'.format(num, res.value))
        self.record(']')

        self.record('\n')

    def record_player_trades_with_other(self, player, to_other, other, to_player):
        """
        $color trades [$number $resources, $number resources] to player:$color for [$number $resources, $number resources]

        the to_resources params are dicts of form {'wood':2,'brick':1}
        """
        self.record('{0} trades '.format(player.color))

        # to_other items
        self.record('[')
        for i, (res, num) in enumerate(to_other.items()):
            if i > 0:
                self.record(',')
            self.record('{0} {1}'.format(num, res.value))
        self.record(']')

        self.record(' to player:{0} for '.format(other.color))

        # to_player items
        self.record('[')
        for i, (res, num) in enumerate(to_player.items()):
            if i > 0:
                self.record(',')
            self.record('{0} {1}'.format(num, res.value))
        self.record(']')

        self.record('\n')

    def record_player_plays_dev_knight(self, player, tile_id, victim):
        """
        $color plays dev card: knight on $hex, steals from $color
        """
        self.recordln('{0} plays dev card: knight on {1}, steals from {2}'.format(
            player.color,
            tile_id,
            victim.color
        ))

    def record_player_plays_dev_monopoly(self, player, resource):
        """
        $color plays dev card: monopoly on $resource

        resource is the lowercase fulltext, eg 'wood', 'wheat', 'brick', 'ore', 'sheep'
        """
        self.recordln('{0} plays dev card: monopoly on {1}'.format(
            player.color,
            resource.value
        ))

    def record_player_plays_dev_victory_point(self, player):
        """
        $color plays dev card: victory point
        """
        self.recordln('{0} plays dev card: victory point'.format(player.color))

    def record_player_plays_dev_road_builder(self, player, node_id_a1, node_id_a2, node_id_b1, node_id_b2):
        """
        $color plays dev card: road builder, builds from $location to $location and $location to $location
        """
        self.recordln('{0} plays dev card: road builder, builds from {1} to {2} and {3} to {4}'.format(
            player.color,
            node_id_a1,
            node_id_a2,
            node_id_b1,
            node_id_b2
        ))

    def record_player_ends_turn(self, player):
        """
        $color ends turn
        """
        self.recordln('{0} ends turn'.format(player.color))

    def record_player_wins(self, player):
        self.recordln('{0} wins'.format(player.color))

    def _record_board_terrain(self, terrain):
        self.recordln('terrain: {0}'.format(' '.join(t.value for t in terrain)))

    def _record_board_numbers(self, numbers):
        self.recordln('numbers: {0}'.format(' '.join(str(n.value) for n in numbers)))

    def _record_board_ports(self, ports):
        self.recordln('ports: {0}'.format(' '.join(p.value for p in ports)))

    def _record_players(self, players):
        self.recordln('players: {0}'.format(len(players)))
        players = list(players)
        players.sort(key=lambda p: p.seat)
        for p in players:
            self.player_names.append(p.name)
            self.recordln('name: {0}, color: {1}, seat: {2}'.format(p.name, p.color, p.seat))

