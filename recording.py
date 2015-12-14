import datetime


class GameRecord(object):
    version = '0.0.1'

    def __init__(self, directory):
        self.record_str = str()
        self.directory = directory
        self.timestamp = datetime.datetime.now()

    def record(self, content):
        self.record_str += content

    def recordln(self, content):
        self.record_str += '{0}\n'.format(content)

    def flush(self):
        # write to timestamp file in self.directory
        pass

    def record_initial_layout(self, players, resources, numbers, ports):
        self.recordln('CatanGameRecord v{0}'.format(GameRecord.version))
        self.recordln('timestamp: {0}'.format(self.timestamp))
        self._set_players(players)
        self._set_board_resources(resources)
        self._set_board_numbers(numbers)
        self._set_board_ports(ports)
        self.record('...CATAN!\n\n')

    '''
    $color rolls $number
    '''
    def record_roll(self, player, roll):

        self.recordln('{0} rolls {1}'.format(player.color, roll))

    '''
    $color is robbed
    '''
    def record_is_robbed(self, player):
        self.recordln('{0} is robbed'.format(player.color))

    '''
    $color moves robber to $hex, steals from $color
    '''
    def record_moves_robber_and_steals(self, player, tile_id, victim):
        self.recordln('{0} moves robber to {1}, steals from {2}'.format(
            player.color,
            tile_id,
            victim.color
        ))

    '''
    $color buys settlement, builds at $location
    '''
    def record_buys_settlement(self, player, node_id):
        self.recordln('{0} buys settlement, builds at {1}'.format(
            player.color,
            node_id
        ))

    '''
    $color buys city, builds at $location
    '''
    def record_buys_city(self, player, node_id):
        self.recordln('{0} buys city, builds at {1}'.format(
            player.color,
            node_id
        ))

    '''
    $color buys dev card
    '''
    def record_buys_dev_card(self, player):
        self.recordln('{0} buys dev card'.format(
            player.color
        ))

    '''
    $color buys road, builds from $location to $location
    '''
    def record_buys_road(self, player, node_id_1, node_id_2):
        self.recordln('{0} buys road, builds from {1} to {2}'.format(
            player.color,
            node_id_1,
            node_id_2
        ))

    '''
    $color trades $number $resources[, $number resources]* to port:$port for $number $resources[, $number resources]*

    the to_resources params are dicts of form {'wood':2,'brick':1}
    '''
    def record_trade_with_port(self, player, to_port, port, to_player):
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

    '''
    $color trades [$number $resources, $number resources] to player:$color for [$number $resources, $number resources]

    the to_resources params are dicts of form {'wood':2,'brick':1}
    '''
    def record_trade_with_player(self, player, to_other, other, to_player):
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

    '''
    $color plays dev card: knight on $hex, steals from $color
    '''
    def record_plays_dev_knight(self, player, tile_id, victim):
        self.recordln('{0} plays dev card: knight on {1}, steals from {2}'.format(
            player.color,
            tile_id,
            victim.color
        ))

    '''
    $color plays dev card: monopoly on $resource

    resource is the lowercase fulltext, eg 'wood', 'wheat', 'brick', 'ore', 'sheep'
    '''
    def record_plays_dev_monopoly(self, player, resource):
        self.recordln('{0} plays dev card: monopoly on {1}'.format(
            player.color,
            resource
        ))

    '''
    $color plays dev card: victory point
    '''
    def record_plays_dev_victory_point(self, player):
        self.recordln('{0} plays dev card: victory point'.format(player.color))

    '''
    $color plays dev card: road builder, builds from $location to $location and $location to $location
    '''
    def record_plays_dev_road_builder(self, player, node_id_a1, node_id_a2, node_id_b1, node_id_b2):
        self.recordln('{0} plays dev card: road builder, builds from {1} to {2} and {3} to {4}'.format(
            player.color,
            node_id_a1,
            node_id_a2,
            node_id_b1,
            node_id_b2
        ))

    '''
    $color ends turn
    '''
    def record_ends_turn(self, player):
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

