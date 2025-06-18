# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: C:\Users\yuyan\Documents\life-series-simulator\gameElements.py
# Bytecode version: 3.10.0rc2 (3439)
# Source timestamp: 2023-09-04 04:30:04 UTC (1693801804)

pass
from random import choice, randint
from gameMessages.trapTypes import TYPES
MAX_STEALTH = 7
MAX_LETHAL = 7

class Trap:
    pass

    def __init__(self, player):
        self.player = player
        self.type = choice(TYPES)
        self.stealth = randint(2, MAX_STEALTH)
        self.lethality = randint(2, MAX_LETHAL)

    def set_message(self):
        pass
        return self.type['set']

    def get_player(self):
        pass
        return self.player

    def trigger(self, num, tripped):
        pass
        if not tripped:
            if num >= MAX_STEALTH or randint(num, MAX_STEALTH) > self.stealth:
                return (False, self.type['disarm'], self.player)
            if num >= MAX_LETHAL or randint(num, MAX_LETHAL) > self.lethality:
                return (False, self.type['escape'], self.player)
        return (True, self.type['kill'], self.player)