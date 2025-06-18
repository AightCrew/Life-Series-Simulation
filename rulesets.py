pass
from lifesim.signallers import sig
from random import randint, choice

class ThirdLife:
    pass

    def __init__(self, game, lives, boogey, lifesteal):
        self.game = game
        self.lives = lives
        self.boogey = boogey
        self.lifesteal = lifesteal

    def start(self, players):
        return

    def set_lives(self):
        pass
        return self.lives


    def set_time(self):
        #Time doesn't matter so I put in a random time so it doesn't return None
        return 10

    def player_death(self, p):
        pass
        p.inc_deaths()
        return self.player_reduce_lives(p, 1)

    def lifesteal_enabled(self):
        return self.lifesteal

    def player_reduce_lives(self, p, n):
        p.set_lives(p.get_lives() - n)
        if p.get_lives() == 0:
            #Returns true if eliminated
            return True
        if p.get_lives() == 1:
            sig.player_red(p)
            p.set_hostile(True)
            #Red players become hostile
            if p.is_boogey():
                p.cure_boogey()
                sig.boogey_fail(p)
                #Fails boogey if red
        else:
            p.set_hostile(False)
        return False

    def player_kill(self, p1):
        pass
        return self.player_death(p1)

    def assign_boogey(self, players):
        if self.boogey:
            return None
        if all((x.is_hostile() for x in players)) or len(list(filter(lambda x: x.get_lives() > 1, players))) < 2:
            return None
        chance = len(players) // 2 + 1
        base = chance
        while randint(1, base) <= chance:
            boogey = choice(players)
            if boogey.get_lives() != 1 and (not boogey.is_boogey()):
                boogey.set_boogey()
                sig.boogey_pick(boogey)
                chance = chance / 5 * 3
    def give_life(self, p1, p2):
        return False

    def assign_soulmates(self, players):
        return players

    def can_ally(self, players):
        return True

class LastLife:
    pass

    def __init__(self, game, lives, boogey, lifesteal):
        self.game = game
        self.lives = lives
        self.boogey = boogey
        self.lifesteal = lifesteal

    def start(self, players):
        sig.lives(players)
        sig.cont()

    def set_lives(self):
        pass
        return randint(2, self.lives)

    def set_time(self):
        return 10
    def player_death(self, p):
        pass
        p.inc_deaths()
        return self.player_reduce_lives(p, 1)

    def lifesteal_enabled(self):
        return self.lifesteal

    def player_reduce_lives(self, p, n):
        if n == 0:
            return
        p.set_lives(p.get_lives() - n)
        if p.get_lives() == 0:
            return True
        if p.get_lives() == 1:
            sig.player_red(p)
            alliance = p.get_alliance()
            #Former alliance is stored
            if alliance is not None:
                p.set_formerAlliance(p.get_alliance())
                sig.alliance_leave(p, alliance.get_name())
                p.leave_alliance([])
            p.set_hostile(True)
            if p.is_boogey():
                p.cure_boogey()
                sig.boogey_fail(p)
        else:
            p.set_hostile(False)
        #If player gains life, they go back to original alliance
        if p.get_lives()>1 and p.get_alliance() and p.get_alliance().get_name()!= 'Gone' and p.get_formerAlliance():
            p.set_alliance(p.get_formerAlliance())
            sig.alliance_join(p, p.get_formerAlliance().get_name())
        return False

    def player_kill(self, p1):
        pass
        return self.player_death(p1)

    def assign_boogey(self, players):
        if self.boogey:
            return None
        if all((x.is_hostile() for x in players)) or len(list(filter(lambda x: x.get_lives() > 1, players))) < 2:
            return None
        chance = len(players) // 2 + 1
        base = chance
        while randint(1, base) <= chance:
            boogey = choice(players)
            if boogey.get_lives() != 1 and (not boogey.is_boogey()):
                boogey.set_boogey()
                sig.boogey_pick(boogey)
                chance = chance / 5 * 3

    def give_life(self, p1, p2):
        sig.life_trade(p1, p2)
        p1.set_lives(p1.get_lives() - 1)
        p2.set_lives(p2.get_lives() + 1)
        if not p2.is_boogey():
            p2.set_hostile(False)
        if p2.get_lives() == 2 and p2.get_alliance() != None:
            sig.alliance_leave(p2, p2.get_alliance().get_name())
            p2.leave_alliance(self.game.get_relationships())
        return True

    def assign_soulmates(self, players):
        return players

    def can_ally(self, players):
        return all((p.get_lives() == 1 for p in players)) or all((p.get_lives() != 1 for p in players))

class DoubleLife:
    pass

    def __init__(self, game, lives, boogey, lifesteal):
        self.game = game
        self.lives = lives
        self.boogey = boogey
        self.lifesteal = lifesteal

    def start(self, players):
        sig.soulbounds(players,0)
        sig.cont()

    def set_lives(self):
        pass
        return self.lives

    def set_time(self):
        return 10

    def player_death(self, p):
        if p not in self.game.players:
            return False
        p.inc_deaths()
        if p.get_soulbound() in self.game.players:
            p.get_soulbound().inc_deaths()
        pass
        self.player_reduce_lives(p, 1)
        return self.player_reduce_lives(p.get_soulbound(), 1)

    def lifesteal_enabled(self):
        return self.lifesteal

    def player_reduce_lives(self, p, n):
        if n == 0:
            return
        p.set_lives(p.get_lives() - n)
        if p.get_lives() == 0:
            return True
        if p.get_lives() == 1:
            sig.player_red(p)
            p.set_hostile(True)
            if p.is_boogey():
                p.cure_boogey()
                sig.boogey_fail(p)
        else:
            p.set_hostile(False)
        return False

    def player_kill(self, p1):
        pass
        return self.player_death(p1)

    def assign_boogey(self, players):
        if self.boogey:
            return None
        if all((x.is_hostile() for x in players)) or len(list(filter(lambda x: x.get_lives() > 1, players))) < 2:
            return None
        chance = len(players) // 2 + 1
        base = chance
        while randint(1, base) <= chance:
            boogey = choice(players)
            if boogey.get_lives() != 1 and (not boogey.is_boogey()):
                boogey.set_boogey()
                sig.boogey_pick(boogey)
                chance = chance / 5 * 3

    def give_life(self, p1, p2):
        return False

    def assign_soulmates(self, players):
        assigned = []
        player_copy = players.copy()
        while len(player_copy) > 0:
            p = player_copy[0]
            if p.get_soulbound() != None:
                pass
            assigned.append(p)
            player_copy.remove(p)
            soulbound = choice(players)
            while soulbound.get_soulbound() != None or soulbound == p:
                soulbound = choice(player_copy)
            p.set_soulbound(soulbound)
            soulbound.set_soulbound(p)
            player_copy.remove(soulbound)
        return assigned

    def can_ally(self, players):
        return False

class LimitedLife:
    pass

    def __init__(self, game, lives, boogey, lifesteal):
        self.game = game
        self.lives = lives
        self.boogey = boogey
        self.lifesteal = lifesteal

    def start(self, players):
        return

    def set_lives(self):
        pass
        return 3

    def set_time(self):
        return self.lives

    def player_death(self, p):
        pass
        p.inc_deaths()
        return self.player_reduce_lives(p, 1)

    def lifesteal_enabled(self):
        return self.lifesteal

    def player_reduce_lives(self, p, n):
        """
        If selected hours are 24 than
        Green: >16 hours
        Yellow: >8 hours
        Red: Between 0 and 8 hours
        """
        p.set_time(p.get_time() - n)
        if p.get_time() <= 0:
            p.set_lives(0)
            return True
        if p.get_time()<self.lives/6 and p.is_boogey():
            p.cure_boogey()
            sig.boogey_fail(p)
        if p.get_time() > self.lives *2/3:
            p.set_hostile(False)
            p.set_lives(3)
        elif p.get_time() > self.lives * 1/3:
            p.set_hostile(True)
            p.set_lives(2)
        elif p.get_time() > 0:
            p.set_lives(1)
            p.set_hostile(True)
        return False

    def player_kill(self, p1):
        pass
        return self.player_death(p1)

    def assign_boogey(self, players):
        if self.boogey:
            return None
        if all((x.get_lives()<2 for x in players)) or len(list(filter(lambda x: x.get_lives() > 1, players))) < 2:
            return None
        chance = len(players) // 2 + 1
        base = chance
        while randint(1, base) <= chance:
            boogey = choice(players)
            if boogey.get_lives() != 1 and (not boogey.is_boogey()):
                boogey.set_boogey()
                sig.boogey_pick(boogey)
                chance = chance / 5 * 3

    def give_life(self, p1, p2):
        return False

    def assign_soulmates(self, players):
        return players

    def can_ally(self, players):
        return True