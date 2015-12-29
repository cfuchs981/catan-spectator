import logging
from collections import Counter


class CatanTrade(object):
    def __init__(self, giver=None, getter=None):
        self._give = list()
        self._get = list()
        self._giver = giver
        self._getter = getter

    def give(self, terrain, num=1):
        for _ in range(num):
            logging.debug('terrain={}'.format(terrain))
            self._give.append(terrain)

    def get(self, terrain, num=1):
        for _ in range(num):
            logging.debug('terrain={}'.format(terrain))
            self._get.append(terrain)

    def giver(self):
        return self._giver

    def getter(self):
        return self._getter

    def giving(self):
        """Returns tuples: [(2, Terrain.wood), (1, Terrain.brick)]"""
        logging.debug('give={}'.format(self._give))
        c = Counter(self._give.copy())
        return [(n, t) for t, n in c.items()]

    def getting(self):
        """Returns tuples: [(2, Terrain.wood), (1, Terrain.brick)]"""
        c = Counter(self._get.copy())
        return [(n, t) for t, n in c.items()]

    def set_giver(self, giver):
        """
        :param giver: Player
        """
        self.giver = giver

    def set_getter(self, getter):
        """
        :param getter: Player
        """
        self.getter = getter
