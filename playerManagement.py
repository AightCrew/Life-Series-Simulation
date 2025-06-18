# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: C:\Users\yuyan\Documents\life-series-simulator\playerManagement.py
# Bytecode version: 3.10.0rc2 (3439)
# Source timestamp: 2023-09-02 09:56:25 UTC (1693648585)

pass
from math import ceil
from signallers import sig
REL_CAP = 10

REL_CAP = 10

class Player:
    pass

    def __init__(self, index, name, lives, time):
        self.index = index
        self.name = name
        self.lives = lives
        self.time = time
        self.alliance = None
        self.hostile = False
        self.kills = 0
        self.boogey = False
        self.soulbound = None
        self.deaths = 0
        self.formerAlliance = None
        self.secondLife = False
        
    def set_secondLife(self, can_secondLife):
        if self.secondLife==False and can_secondLife:
            sig.secondLife(self)
            self.secondLife = True
            return True
        else:
            return False
    def get_secondLife(self):
        return self.secondLife
    def set_lives(self, lives):
        self.lives = lives

    def get_index(self):
        return self.index

    def set_formerAlliance(self, alliance):
        self.formerAlliance = alliance

    def get_formerAlliance(self):
        return self.formerAlliance

    def set_time(self, time):
        self.time = time

    def get_time(self):
        return self.time

    def get_name(self):
        return self.name

    def get_lives(self):
        return self.lives

    def set_alliance(self, alliance):
        if alliance:
            self.alliance = alliance
            self.alliance.add_member(self)
        else:
            self.alliance = None

    def get_alliance(self):
        return self.alliance

    def get_alliance_name(self):
        pass
        if self.alliance is not None:
            return self.alliance.getName()
        return 'None'

    def set_hostile(self, hostile):
        self.hostile = hostile

    def is_hostile(self):
        if self.boogey:
            return True
        return self.hostile

    def get_kills(self):
        return self.kills

    def inc_kills(self):
        pass
        self.kills += 1

    def inc_deaths(self):
        pass
        self.deaths+= 1

    def get_deaths(self):
        return self.deaths

    def leave_alliance(self, relations):
        pass
        if self.alliance is not None:
            self.alliance.remove_member(self)
            if relations and self.alliance.disband(relations):
                self.alliance = None
                return True
            self.alliance = None
        return False

    def set_boogey(self):
        self.boogey = True

    def cure_boogey(self):
        self.boogey = False
        if self.get_lives() > 1 or self.time>16:
            self.set_hostile(False)

    def is_boogey(self):
        return self.boogey

    def boogey_bonus(self, bonus):
        if self.boogey:
            return bonus
        return 1

    def get_soulbound(self):
        return self.soulbound

    def set_soulbound(self, soulbound):
        self.soulbound = soulbound

class Alliance:
    pass

    def __init__(self, name):
        self.name = name
        self.members = []
        self.strength = 1

    def get_name(self):
        return self.name

    def get_members(self):
        return self.members

    def add_member(self, p):
        self.members.append(p)

    def remove_member(self, p):
        self.members.remove(p)

    def get_strength(self):
        return self.strength

    def check_stability(self, relations):
        pass
        overall = 0
        while True:
            perceptions = [0] * len(self.members)
            individual = [0] * len(self.members)
            overall = 0
            for i, player in enumerate(self.members):
                for j, target in enumerate(self.members):
                    rel = relations[player.get_index()][target.get_index()]
                    perceptions[j] += rel
            kicked = []
            leaving = []
            for i, val in enumerate(perceptions):
                if val <= -5 * len(self.members):
                    kicked.append(self.members[i])
            for k in kicked:
                k.leave_alliance([])
                sig.alliance_kick(k, self.name)
            for i, player in enumerate(self.members):
                for j, target in enumerate(self.members):
                    rel = relations[player.get_index()][target.get_index()]
                    individual[i] += rel
                    overall += rel
            for i, val in enumerate(individual):
                if val < -5 * len(self.members) and self.members[i] not in kicked:
                    leaving.append(self.members[i])
            for i in leaving:
                i.leave_alliance([])
                sig.alliance_leave(i, self.name)
            if len(kicked) == 0 and len(leaving) == 0:
                break
            if len(self.members) <= 1:
                return True
        if overall < -5 * len(self.members):
            return True
        new_str = ceil(overall / REL_CAP) * 2 + 1
        if new_str > 0:
            self.strength = new_str
            return False
        self.strength = 0
        return False

    def disband(self, relations):
        pass
        if len(self.get_members()) < 1 or self.check_stability(relations):
            for p in self.members:
                p.set_alliance(None)
            sig.alliance_disband(self.name)
            self.name = 'Gone'
            return True
        else:
            return False

    @staticmethod
    def get_alliance_bonus(p1, p2):
        pass
        if p1.get_alliance() == p2.get_alliance:
            return p1.get_alliance().get_strength()
        return 0