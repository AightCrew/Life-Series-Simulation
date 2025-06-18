# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: lifesim.py
# Bytecode version: 3.10.0rc2 (3439)
# Source timestamp: 2023-09-10 10:58:05 UTC (1694343485)

pass
from random import randint, choice, choices, shuffle
from math import ceil, floor, log
from lifesim.playerManagement import Player, Alliance, REL_CAP
from lifesim.rulesets import ThirdLife, LastLife, DoubleLife, LimitedLife
from lifesim.signallers import sig
from lifesim.gameMap import Map
HOURS = 4
class Game:
    pass

    def __init__(self):
        self.game_over = False
        self.rule = None
        self.all = []
        self.players = []
        self.eliminated = []
        self.alliances = []
        self.map = None
        self.relationships = []
        self.session = 0
        self.fixed_alliances = False
    def init(self):
        pass
        self.map = Map(ceil(len(self.players) / 3))
        self.relationships = [None] * len(self.players)
        for i in range(len(self.players)):
            self.relationships[i] = [0] * len(self.players)
        self.rule.start(self.rule.assign_soulmates(self.players))

    def hostileCount(self, players):
        count = 0
        for player in players:
            if player.is_hostile():
                count = count + 1
        return count

    def is_set_alliance(self):
        return self.fixed_alliances

    #Running this causes alliances to never break up
    def set_alliance(self):
        self.fixed_alliances = True

    def add_player(self, name):
        pass
        player = Player(len(self.players), name, self.rule.set_lives(),self.rule.set_time())
        #If a player is already red when starting, they start as hostile
        if player.get_lives()==1:
            player.set_hostile(True)
        self.players.append(player)
        self.all.append(player)

    def get_player(self, name):
        for p in self.all:
            if p.get_name() == name:
                return p
        return None


    def set_rules(self, ruleset):
        pass
        self.rule = ruleset

    def get_relationship(self, play_1, play_2):
        pass
        rel = self.relationships[play_1.get_index()][play_2.get_index()] + Alliance.get_alliance_bonus(play_1, play_2)
        if rel > 0:
            return min(REL_CAP, rel)
        return max(-REL_CAP, rel)

    def get_relationships(self):
        return self.relationships

    def decay_relationships(self):
        pass
        for i, player in enumerate(self.relationships):
            for j in range(0, len(player)):
                val = self.relationships[i][j]
                self.relationships[i][j] -= int(val / abs(val)) if val!= 0 and randint(0, 1) == 0 else 0

    def soulmates_can_fight(self, p1, p2):
        #Checks if soulmates are able to kill each other (only when they're the last 2 remaining)
        return not (
            p1.get_soulbound() == p2 and
            len(self.players) > 2 and
            isinstance(self.rule, DoubleLife)
    )


    def player_elimination(self, player):
        #Eliminates player with the proper death message
        pass
        if isinstance(self.rule, LimitedLife):
            sig.time_elimination(player)
        else:
            sig.player_eliminated(player)
        self.players.remove(player)
        self.eliminated.insert(0, player)
        #REmoves player from alliance
        alliance = player.get_alliance()
        if player.leave_alliance(self.relationships):
            self.alliances.remove(alliance)
        soulbound = player.get_soulbound()
        #Also eliminates soulbound if there is one
        if soulbound is not None:
            player.set_soulbound(None)
            soulbound.set_soulbound(None)
            if soulbound in self.players:
                self.player_elimination(soulbound)

    def generate_conflict_sides(self, attacker, defender, participants):
        pass
        participants.remove(attacker)
        participants.remove(defender)
        if len(participants) == 0:
            self.relationships[attacker.get_index()][defender.get_index()] -= randint(3, 4)
            sig.player_fight([attacker], [defender])
            return ([attacker], [defender])
        attackers = [attacker]
        defenders = [defender]
        for player in participants:
            a_rel = self.get_relationship(player, attacker)
            d_rel = self.get_relationship(player, defender)
            #If a player has a good relationship with the defender they will join them
            if d_rel == REL_CAP or randint(0, REL_CAP - d_rel) == 0:
                defenders.append(player)
            else:  # inserted
                #If a hostile has a bad relationship with the hostile, they will help in killing them
                if player.is_hostile() and (a_rel == REL_CAP or randint(0, REL_CAP - a_rel) == 0):
                    attackers.append(player)
        for defender in defenders:
            for attacker in attackers:
                self.relationships[defender.get_index()][attacker.get_index()] -= randint(3, 4)
        sig.player_fight(attackers, defenders)
        return (attackers, defenders)

    def battle(self, attack, defence):
        pass
        a_sum = 0
        d_sum = 0
        for attacker in attack:
            if isinstance(self.rule, LimitedLife):
                val0= 2 * attacker.get_time()
            else:
                val0 = attacker.get_lives()
            """
            Formula for what player will win
            boogey_bonus(1.4) will return 1.4 if that player is a boogey otherwise it will be 1"""
            a_sum += attacker.boogey_bonus(1.4)/(val0) *(randint(3, 8)) * (1.3 if attacker.is_hostile() else 1) * floor(len(self.players) / 2)
        for defender in defence:
            if isinstance(self.rule, LimitedLife):
                val0= 2 * defender.get_time()+1
            else:
                val0 = defender.get_lives()+1
            d_sum +=(randint(3, 8))/(val0) * defender.boogey_bonus(1.2) * floor(len(self.players) / 2)
        winning, losing, attack_win = (defence, attack, False) if a_sum <= d_sum else (attack, defence, True)
        cured = []
        killed = []
        #print('Attacker sum: ', a_sum, '\nDefender sum: ', d_sum)
        already_penalized = set()
        for original_player in losing[:]:
            if original_player not in self.players:
                continue  # already eliminated

            player = original_player
            opponent = winning
            switched = False

            if player not in self.players:
                continue  # Already eliminated this session

            if randint(0, 2) ==1 or len(cured) == len(winning):
                people = [p for p in winning if p not in killed and p not in cured]
                #40% chance for one of the winning players to die from one of the losing players and a switch to happen
                if randint(0,4)<1 and len(cured)!=len(winning) and len(winning)>len(killed) and people:
                    switch = True
                    opponent= losing
                    #Can't choose a player that has already been killed
                    player = choice(winning)
                    while player in killed:
                        player = choice(winning)
                    killed.append(player)
                    if player.get_soulbound():
                        killed.append(player.get_soulbound())
                else:
                    sig.player_escape(player, winning, attack_win)
                    continue
            valid_attackers = [a for a in opponent if a in self.players and self.soulmates_can_fight(a, player) and a not in killed and a not in cured]
            if not valid_attackers:
                # if no valid attacker, just let them escape
                sig.player_escape(player, opponent, attack_win)
                continue
            if player.get_lives()==1 and self.hostileCount(self.players)<len(self.players)/3:
                #If it's too early in the game for an elimination, let the red player escape
                sig.player_escape(player, opponent, attack_win)
                continue
            if player in already_penalized:
                #If the soulmate has already died, they shouln't have another death as well
                sig.player_escape(player, opponent, attack_win)
                continue

            attacker = choice(valid_attackers)

            boogey = False
            soulmate = player.get_soulbound()
            if soulmate and soulmate in losing:
                already_penalized.add(soulmate)
            killed.append(player)
            sig.player_killed(player, attacker)
            originalLives = player.get_lives()
            #Checks if player is a boogey and their kill follows boogey rules
            if attacker.is_boogey() and (player.get_lives()>1 or (isinstance(self.rule, LimitedLife) and attacker.get_lives()<=originalLives)):
                attacker.cure_boogey()
                sig.boogey_cure(attacker)
                boogey = True
                cured.append(attacker)

                if isinstance(self.rule, LimitedLife):
                    #Players lose an extra hour if they die from the boogey
                    if self.rule.player_reduce_lives(player, 1):
                        self.player_elimination(player)
                    sig.time_change(player,2)

            self.relationships[player.get_index()][attacker.get_index()] -= randint(1, 3) + (ceil(REL_CAP / 3) if player.get_alliance() is not None and player.get_alliance() == attacker.get_alliance() else 0)
            if self.rule.player_death(player):
                self.player_elimination(player)

            #Checks if lifesteal is enabled for Limited Life
            if self.rule.lifesteal_enabled() and isinstance(self.rule, LimitedLife) and (not isinstance(self.rule, LimitedLife) or attacker.get_lives()<=originalLives):
                #Boogeys gain 1 hour instead of 30 minutes
                n = -1 if boogey else -.5
                self.rule.player_reduce_lives(attacker,n)
                sig.time_change(attacker,n)
            #Checks if lifesteal is enabled and the hostile has at least 2 lives less than the victim
            elif player.get_lives()>1 and attacker.get_lives()<player.get_lives() and self.rule.lifesteal_enabled():
                self.rule.player_reduce_lives(attacker,-1)
                soulbound = attacker.get_soulbound()
                if soulbound!= None:
                    self.rule.player_reduce_lives(soulbound,-1)
                    soulbound.set_hostile(False)
                    sig.life_gain(soulbound)
                sig.life_gain(attacker)
                attacker.set_hostile(False)
                cured.append(attacker)
            attacker.inc_kills()



    def generate_conflict(self, participants, hostiles):
        pass
        for hostile in hostiles:
            if not hostile.is_hostile():
                continue  # Skip if cured earlier this session
            if randint(0,1)==0 and not hostile.is_boogey():
                continue
                #Reduce amount of conflicts otherwise it's too chaotic

            best_target = None
            lowest_val = float('inf')

            for target in participants:
                if hostile.get_index() == target.get_index():
                    continue
                if not self.soulmates_can_fight(hostile, target):
                    continue
                if hostile.is_boogey() and target.get_lives() == 1:
                    continue  # Boogeymen should not attack red players
                if isinstance(self.rule, LimitedLife) and hostile.get_lives()>target.get_lives():
                    #Yellows can't attack reds
                    continue
                if target.get_lives()==1 and self.hostileCount(self.players)<len(self.players)/2.4:
                    #Reds should ideally not be killing each other until the endgame
                    continue
                if target.get_alliance==hostile.get_alliance() and len(self.players)>len(hostile.get_alliance().get_members()) and randint(0,9)>0:
                    #Alliances should ideally not kill each other unless their the only ones left, but still leave possibility of betrayal
                    continue

                rel = self.get_relationship(hostile, target)
                if rel == -REL_CAP or len(self.players) < 4:
                    val = 0
                else:
                    #Calculates how much of a target that player is
                    aggression = (target.get_time() if isinstance(self.rule, LimitedLife) else target.get_lives()) * (4 if hostile.is_boogey() else 3)/(10 if target.get_alliance()==hostile.get_alliance else 1)
                    val = rel - aggression -randint(0,2)

                if val < lowest_val:
                    lowest_val = val
                    best_target = target

            if best_target is not None:
                side1, side2 = self.generate_conflict_sides(hostile, best_target, participants)
                self.battle(side1, side2)
                return True

        else:  # inserted
            return False

    def generate_single_player_event(self, player):
        pass
        if player.get_alliance() is None:
            indices = []
            max_val = -REL_CAP
            if player.get_lives() == 1:
                indices = [i for i, val in enumerate(self.relationships[player.get_index()]) if val >= 0]
                indices.sort()
                if len(indices) > 0:
                    max_val = indices[0]
            else:  # inserted
                max_val = max(self.relationships[player.get_index()])
                indices = [i for i, val in enumerate(self.relationships[player.get_index()]) if val == max_val]
                shuffle(indices)
            #Player joins alliance
            if max_val > -ceil(REL_CAP / 2) and (max_val >= ceil(REL_CAP / 2) or randint(0, max(1, ceil(REL_CAP / 4) - max_val // 2)) - floor(20 / self.session)) <= 0:
                for index in indices:
                    alliance = self.all[index].get_alliance()
                    if alliance and (player.get_lives()!= 1 or (player.get_lives() == 1 and alliance.get_members()[0].get_lives() == 1)) and (len(alliance.get_members()) < 5 and player.get_lives()>0) and not self.fixed_alliances:
                        sig.alliance_join(player, alliance.get_name())
                        player.set_alliance(alliance)
                        return
        if  True:
            if player.is_hostile() and randint(0, 1) == 0 and player.get_lives()>0:
                sig.player_trap(self.map.set_trap(player), player, [], False)
            else:  # inserted
                if len(self.eliminated) > 0 and randint(0, REL_CAP * 2) == 0:
                    sig.event_deadloot([player], choice(self.eliminated))
                else:  # inserted
                    sig.filler([player], [], [], self.session)

    def generate_event(self, participants, sector):
        pass
        def relation_update(side1, side2, sign, amount):
            for play1 in side2:
                for play2 in side1:
                    index1, index2 = (play1.get_index(), play2.get_index())
                    self.relationships[index1][index2] += sign * randint(amount[0], amount[1])
                    if sign > 0:
                        self.relationships[index2][index1] += randint(amount[0], amount[1])

        def alliance_event(participants, type_of_inter):
            alliance = choice(self.alliances)
            sig.event_alliance(participants, alliance.get_name(), type_of_inter)
            return alliance.get_members()
        if sector.get_trap():
            if len(self.players) > len(participants):
                tripped = bool(sector.get_trap_setter() in participants and randint(0, 5) == 0)
                if sector.get_trap_setter() not in participants or tripped:
                    kill, text, setter = sector.trigger_trap(len(participants), tripped)
                    sig.player_trap(text, setter, participants, kill)
                    if kill:
                        found = choice([True, False])
                        already_penalized = set()
                        for player in participants:
                            originalLives = player.get_lives()
                            if player not in self.players:
                                continue  # Already eliminated

                            if player in already_penalized:
                                continue  # skip — already handled via soulmate pair

                            if found:
                                self.relationships[player.get_index()][setter.get_index()] -= 3 + (
                                    floor(REL_CAP / 3)
                                    if player.get_alliance() is not None and player.get_alliance() == setter.get_alliance()
                                    else 0
                                )

                            if self.rule.player_death(player):
                                self.player_elimination(player)

                            soulmate = player.get_soulbound()
                            if soulmate and soulmate in participants:
                                #Makes it so soulmate pair doesn't get penalized twice
                                already_penalized.add(soulmate)
                            #Same think as the battle version
                            if setter!= player:
                                boogey = False
                                if setter.is_boogey() and (originalLives>1 or (isinstance(self.rule, LimitedLife) and setter.get_lives()<=originalLives)):
                                    setter.cure_boogey()
                                    boogey = True
                                    sig.boogey_cure(setter)
                                    if isinstance(self.rule, LimitedLife):
                                        if self.rule.player_reduce_lives(player, 1):
                                            self.player_elimination(player)
                                        sig.time_change(player,2)
                                if setter.get_time()>0 and self.rule.lifesteal_enabled() and isinstance(self.rule, LimitedLife) and not setter.get_lives()>originalLives:
                                    n = -1 if boogey else -.5
                                    self.rule.player_reduce_lives(setter,n)
                                    sig.time_change(setter,n)
                                elif player.get_lives()>1 and  0<setter.get_lives()<player.get_lives() and self.rule.lifesteal_enabled():
                                    self.rule.player_reduce_lives(setter,-1)
                                    soulbound = setter.get_soulbound()
                                    if soulbound!= None:
                                        self.rule.player_reduce_lives(soulbound,-1)
                                        sig.life_gain(soulbound)
                                    sig.life_gain(setter)
                                setter.inc_kills()
        elif len(participants) < 4 and len(self.alliances) > 0 and (randint(0, HOURS * 6) == 0):
            pos = randint(1, 6)
            match pos:
                case 1 | 2:
                    alliance_event(participants, 'ip')
                case 3 | 4:
                    alliance_event(participants, 'in')
                case 5:
                    alliance_event(participants, 'mp')
                case 6:
                    alliance_event(participants, 'mn')

        else:  # inserted
            if len(participants) == 1:
                if(participants[0].get_lives()>0):
                    self.generate_single_player_event(participants[0])
            else:  # inserted
                #Creates alliances
                if (
                    len(self.players) > len(participants)
                    and all(p.get_alliance() is None for p in participants)
                    and self.rule.can_ally(participants)
                    and not self.fixed_alliances
                ):
                    #Makes sure max 4 when created
                    while len(participants)>4:
                        player = choice(participants)
                        participants.remove(player)
                    name = sig.alliance_create(participants)
                    if name is not None:
                        print("Alliance created: ", name)
                        ally = Alliance(name)
                        for player in participants:
                            player.set_alliance(ally)
                        self.alliances.append(ally)

                elif (
                    len(participants) == 2
                    and participants[0].get_lives() > 2
                    and (participants[0].get_lives() > participants[1].get_lives() + 1)
                    and (
                        randint(0, REL_CAP + 1 - self.get_relationship(participants[0], participants[1]))
                        < participants[0].get_lives() * 1.5
                    )
                    and self.rule.give_life(participants[0], participants[1])
                ):
                    relation_update([participants[0]], [participants[1]], 1, [3, 5])
                    return

                side1, side2 = self.generate_sides(participants)
                event_type = randint(1, 15)  # Assign before using match-case

                match event_type:
                    case 1 | 2 | 3 | 4 | 5:
                        if len(self.eliminated) > 0 and randint(0, REL_CAP * 2) == 0:
                            sig.event_deadloot(participants, choice(self.eliminated))
                        else:
                            sig.filler(participants, side1, side2, self.session)

                    case 6 | 7:
                        sig.event(side1, side2, 'ip')
                        relation_update(side1, side2, 1, [1, 2])

                    case 8 | 9:
                        sig.event(side1, side2, 'in')
                        relation_update(side1, side2, -1, [1, 2])

                    case 10 | 11:
                        sig.event(side1, side2, 'mp')
                        relation_update(side1, side2, 1, [2, 4])

                    case 12 | 13:
                        sig.event(side1, side2, 'mn')
                        relation_update(side1, side2, -1, [2, 4])

                    case 14 | 15:
                        for player in side1:
                            #Makes sure players don't get eliminated too early
                            if player.get_lives()<2 and not isinstance(self.rule, LimitedLife) and self.hostileCount(self.players)>len(self.players)/2.4:
                                side1.remove(player)
                        if side1:
                            sig.player_death(side1)

                        already_penalized = set()

                        for player in side1:
                            if player in already_penalized:
                                continue
                            soulmate = player.get_soulbound()
                            if soulmate and soulmate in side1:
                                already_penalized.add(soulmate)

                            if self.rule.player_death(player):
                                self.player_elimination(player)


                    case _:
                        pass  # Handle unexpected cases gracefully
    def run_day(self):
        pass
        for player in self.players:
            soulmate = player.get_soulbound()
            if soulmate and soulmate in self.players:
                #Makes sure soulbounds always have good relationship
                self.relationships[player.get_index()][soulmate.get_index()] = REL_CAP
                self.relationships[soulmate.get_index()][player.get_index()] = REL_CAP
        if not isinstance(self.rule, DoubleLife) and self.fixed_alliances:
            #Makes sure fixed alliances have good relationships
            for alliance in self.alliances:
                for p1 in alliance.get_members():
                    for p2 in alliance.get_members():
                        self.relationships[p1.get_index()][p2.get_index()]= REL_CAP
        self.session += 1
        self.map.update_sectors(ceil(len(self.players) / 3))
        sig.game_next_sesh(self.session)
        self.rule.assign_boogey(self.players)


        for _ in range(0, floor(HOURS * (log(len(self.all) / len(self.players)) + 1))):
            if self.run_hour(self.map.allocate_sector(self.players)):
                self.game_over = True
                if len(self.players) > 0:
                    winner = self.players[0]
                else:
                    winner = self.eliminated[0]  # Last person to die = first in eliminated list
                return True
        else:  # inserted
            if self.session % 3:
                self.decay_relationships()
            for player in self.players:
                if player.is_boogey():
                    #If a player is boogey and they fail, take away a life or reduce 2 hours (going to red is too much, only one person failed in the actual series and that was intentional)
                    if isinstance(self.rule, LimitedLife):
                        player.cure_boogey()
                        self.rule.player_reduce_lives(player,2)
                        sig.time_change(player,2)
                    else:
                        sig.boogey_end_fail(player)
                        self.rule.player_reduce_lives(player,1)
                        player.cure_boogey()
                        if isinstance(self.rule, DoubleLife):
                            self.rule.player_reduce_lives(player.get_soulbound(),1)

            for alliance in self.alliances:
                if alliance.disband(self.relationships):
                    self.alliances.remove(alliance)
            sig.cont()
            #Displays standings
            if isinstance(self.rule, DoubleLife):
                sig.soulbounds(self.players,self.session)
            elif isinstance(self.rule, LimitedLife):
                sig.timesStanding(self.players, self.alliances, self.session)
            else:
                sig.stats(self.players, self.alliances, self.session)
            sig.cont()
            return False
    def run_hour(self, sectors):
        result = False
        for sector in sectors:
            hostile = [i for i in sector.get_hostile() if i not in self.eliminated]
            participants = [i for i in sector.get_players() if i not in self.eliminated]
            if len(participants) == 0:
                continue
            if len(hostile) == 0 or not self.generate_conflict(participants, hostile):
                self.generate_event(participants, sector)
            if len(self.players) < 2:
                result = True
        else:  # inserted
            if result == False:
                for alliance in self.alliances:
                    if alliance.disband(self.relationships):
                        self.alliances.remove(alliance)
                result = False
        if isinstance(self.rule, LimitedLife):
            shuffle(self.players)
            for player in self.players:
                if self.rule.player_reduce_lives(player, .5):
                    #Reduces players lives by 30 minutes (I know it should be an hour but that would just be too much, I've tried it)
                    self.player_elimination(player)
        #Starts a war
        valid_alliances = [a for a in self.alliances if self.hostileCount(a.get_members())>=len(a.get_members())/2]
        if len(valid_alliances)>1 and randint(0,3)==0:
            alliance1 = choice(valid_alliances)
            alliance2 = choice(valid_alliances)
            while alliance1 == alliance2:
                alliance2 = choice(valid_alliances)
            sig.alliance_war(alliance1.get_name(), alliance2.get_name())
            valid_attackers = [a for a in alliance1.get_members() if a.is_hostile()]
            self.battle(valid_attackers, alliance2.get_members())
        return result

    @staticmethod
    def generate_sides(participants):
        pass
        player_set = set(participants)
        side1 = set(choices(participants, k=randint(1, len(participants) - 1)))
        side2 = list(player_set - side1)
        side1 = list(side1)
        return (side1, side2)