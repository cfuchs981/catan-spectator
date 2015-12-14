import datetime


class GameRecord(object):
    """
    class GameRecord introduces a machine-parsable, human-readable record of all actions made in a game of Catan.

    Each record contains all publicly known information in the game.
    Each record is sufficient to 'replay' a game.

    Use #dump to get the record as a string.
    Use #flush to write the record to a file.
    """
    version = '0.0.1'

    def __init__(self, directory=None):
        self._record_str = str()
        self.directory = directory
        self.timestamp = datetime.datetime.now()

    def record(self, content):
        """
        Writes a string to the record
        """
        self._record_str += content

    def recordln(self, content):
        """
        Writes a string to the record, appending a newline
        """
        self._record_str += '{0}\n'.format(content)

    def dump(self):
        """
        Dumps the current record to a string, and returns it
        """
        return self._record_str

    def flush(self, filename=None):
        """
        Writes the current record to a file, and returns the file descriptor
        """
        # write to timestamp file in self.directory
        pass

    def record_initial_layout(self, players, resources, numbers, ports):
        """
        Begins a game recording.

        :param players: set of 3 or (ideally) 4 #Players
        :param resources: list of 19 resource types as defined in #models (eg resource.WOOD)
        :param numbers: list of 19 numbers, 1 each of (2,12), 2 each of all others
        :param ports: list of 9 ports as defined in #models (eg port.THREE_FOR_ONE)
        """
        self.recordln('CatanGameRecord v{0}'.format(GameRecord.version))
        self.recordln('timestamp: {0}'.format(self.timestamp))
        self._set_players(players)
        self._set_board_resources(resources)
        self._set_board_numbers(numbers)
        self._set_board_ports(ports)
        self.record('...CATAN!\n\n')

    def record_pregame(self, players, resources, numbers, ports):
        """
        Alias for #record_initial_layout
        """
        self.record_initial_layout(players, resources, numbers, ports)

    def record_roll(self, player, roll):
        """
        $color rolls $number
        """
        self.recordln('{0} rolls {1}'.format(player.color, roll))

    def record_is_robbed(self, player):
        """
        $color is robbed
        """
        self.recordln('{0} is robbed'.format(player.color))

    def record_moves_robber_and_steals(self, player, tile_id, victim):
        """
        $color moves robber to $hex, steals from $color
        """
        self.recordln('{0} moves robber to {1}, steals from {2}'.format(
            player.color,
            tile_id,
            victim.color
        ))

    def record_buys_settlement(self, player, node_id):
        """
        $color buys settlement, builds at $location
        """
        self.recordln('{0} buys settlement, builds at {1}'.format(
            player.color,
            node_id
        ))

    def record_buys_city(self, player, node_id):
        """
        $color buys city, builds at $location
        """
        self.recordln('{0} buys city, builds at {1}'.format(
            player.color,
            node_id
        ))

    def record_buys_dev_card(self, player):
        """
        $color buys dev card
        """
        self.recordln('{0} buys dev card'.format(
            player.color
        ))

    def record_buys_road(self, player, node_id_1, node_id_2):
        """
        $color buys road, builds from $location to $location
        """
        self.recordln('{0} buys road, builds from {1} to {2}'.format(
            player.color,
            node_id_1,
            node_id_2
        ))

    def record_trade_with_port(self, player, to_port, port, to_player):
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
            self.record('{0} {1}'.format(num, res))
        self.record(']')

        self.record(' to port:{0} for '.format(port))

        # to_player items
        self.record('[')
        for i, (res, num) in enumerate(to_player.items()):
            if i > 0:
                self.record(',')
            self.record('{0} {1}'.format(num, res))
        self.record(']')

        self.record('\n')

    def record_trade_with_player(self, player, to_other, other, to_player):
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
            self.record('{0} {1}'.format(num, res))
        self.record(']')

        self.record(' to player:{0} for '.format(other.color))

        # to_player items
        self.record('[')
        for i, (res, num) in enumerate(to_player.items()):
            if i > 0:
                self.record(',')
            self.record('{0} {1}'.format(num, res))
        self.record(']')

        self.record('\n')

    def record_plays_dev_knight(self, player, tile_id, victim):
        """
        $color plays dev card: knight on $hex, steals from $color
        """
        self.recordln('{0} plays dev card: knight on {1}, steals from {2}'.format(
            player.color,
            tile_id,
            victim.color
        ))

    def record_plays_dev_monopoly(self, player, resource):
        """
        $color plays dev card: monopoly on $resource

        resource is the lowercase fulltext, eg 'wood', 'wheat', 'brick', 'ore', 'sheep'
        """
        self.recordln('{0} plays dev card: monopoly on {1}'.format(
            player.color,
            resource
        ))

    def record_plays_dev_victory_point(self, player):
        """
        $color plays dev card: victory point
        """
        self.recordln('{0} plays dev card: victory point'.format(player.color))

    def record_plays_dev_road_builder(self, player, node_id_a1, node_id_a2, node_id_b1, node_id_b2):
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

    def record_ends_turn(self, player):
        """
        $color ends turn
        """
        self.recordln('{0} ends turn'.format(player.color))

    def record_win(self, player):
        self.recordln('{0} wins'.format(player.color))

    def _set_board_resources(self, resources):
        self.record('resources: {0}'.format(' '.join(resources)))

    def _set_board_numbers(self, numbers):
        self.record('numbers: {0}'.format(' '.join(numbers)))

    def _set_board_ports(self, ports):
        self.record('ports: {0}'.format(' '.join(ports)))

    def _set_players(self, players):
        self.record('players: ')
        for p in players:
            self.record('[seat: {0}, color: {1}, name: {2}]'.format(p.seat, p.color, p.name))
        self.record('\n')

