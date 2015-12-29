import logging
from collections import Counter


class CatanTrade(object):
    def __init__(self, giver=None, getter=None):
        if giver is None or getter is None:
            logging.critical('Initializing catan trade with giver={}, getter={}, returning None'.format(giver, getter))
        self._give = list()
        self._get = list()
        self._giver = giver
        self._getter = getter

    def give(self, terrain, num=1):
        for _ in range(num):
            self._give.append(terrain)

    def get(self, terrain, num=1):
        for _ in range(num):
            self._get.append(terrain)

    def giver(self):
        return self._giver

    def getter(self):
        return self._getter

    def giving(self):
        """Returns tuples: [(2, Terrain.wood), (1, Terrain.brick)]"""
        c = Counter(self._give.copy())
        return [(n, t) for t, n in c]

    def getting(self):
        """Returns tuples: [(2, Terrain.wood), (1, Terrain.brick)]"""
        c = Counter(self._get.copy())
        return [(n, t) for t, n in c]
