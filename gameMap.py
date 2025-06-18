# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: C:\Users\yuyan\Documents\life-series-simulator\gameMap.py
# Bytecode version: 3.10.0rc2 (3439)
# Source timestamp: 2023-05-29 10:21:22 UTC (1685355682)

pass
import random
from lifesim.gameElements import Trap

class Map:
    pass

    def __init__(self, numsectors):
        self.numsectors = numsectors
        self.sectors = []
        for _ in range(0, numsectors):
            self.sectors.append(Sector())

    def update_sectors(self, num):
        pass
        while num < self.numsectors:
            trap = self.sectors.pop().get_trap()
            if trap:
                sec = random.choice(self.sectors)
                sec.add_trap(trap)
            self.numsectors -= 1
    def allocate_sector(self, players):
        pass
        for sector in self.sectors:
            sector.clear_players()
        for player in players:
            self.sectors[random.randrange(0, self.numsectors)].add_player(player)
        return self.sectors

    def set_trap(self, player):
        pass
        trap = Trap(player)
        sec = random.choice(self.sectors)
        sec.add_trap([trap])
        return trap.set_message()

class Sector:
    pass

    def __init__(self):
        self.players = []
        self.hostile = []
        self.trap = []

    def add_player(self, player):
        pass
        if player.is_hostile():
            self.hostile.insert(random.randint(0, len(self.hostile)), player)
        self.players.insert(random.randint(0, len(self.players)), player)

    def shuffle_players(self):
        pass
        random.shuffle(self.players)

    def clear_players(self):
        pass
        self.players = []
        self.hostile = []

    def get_players(self):
        pass
        return self.players

    def get_hostile(self):
        pass
        return self.hostile

    def get_trap(self):
        pass
        return self.trap

    def get_trap_setter(self):
        pass
        if len(self.trap) > 0:
            return self.trap[0].get_player()

    def add_trap(self, trap):
        pass
        self.trap += trap
        random.shuffle(self.trap)

    def trigger_trap(self, num, tripped):
        pass
        trap = self.trap.pop(0)
        return trap.trigger(num, tripped)