# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: C:\Users\yuyan\Documents\life-series-simulator\signallers.py
# Bytecode version: 3.10.0rc2 (3439)
# Source timestamp: 2023-09-10 10:41:32 UTC (1694342492)

pass
import io
import sys
from random import randint, choice
from functools import reduce
from os import system
import lifesim.gameMessages.fillerEarly as fillEarly
import lifesim.gameMessages.filler as filler
import lifesim.gameMessages.playerDeath as playerDeath
import lifesim.gameMessages.playerKill as playerKill
import lifesim.gameMessages.minorPositive as minPos
import lifesim.gameMessages.minorNegative as minNeg
import lifesim.gameMessages.majorPositive as majPos
import lifesim.gameMessages.majorNegative as majNeg
import lifesim.gameMessages.allianceName as allyName
import lifesim.gameMessages.allianceInteract as allyInt
import lifesim.gameMessages.standardMessages as standMsg
import os
#if os.name == 'nt':  # Only run on Windows
#    os.system('color')
import re
import html

def ansi_to_html(text):
    ansi_map = {
        '91': 'orangeRed',
        '92': 'lime',
        '93': 'yellow',
        '94': 'cadetBlue',
        '95': 'magenta',
        '96': 'cyan',
        '31': 'fireBrick',
        '32': 'green',
        '33': 'yellow',
        '34': 'cadetBlue',
        '35': 'magenta',
        '36': 'cyan',
        '90': 'gray',
        '0': 'reset'
    }

    # Escape HTML special characters first
    text = html.escape(text)

    def repl(match):
        code = match.group(1)
        if code == '0':
            return '</span>'
        color = ansi_map.get(code, 'inherit')
        return f'<span style="color:{color}">'

    return re.sub(r'\x1b\[(\d+)m', repl, text)

class bc:
    ENDC = '\033[0m'
    RED = '\033[31m'
    YELLOW = '\033[33m'
    GREEN = '\033[92m'
    DARKGREEN = '\033[32m'
    PURPLE = '\033[95m'
    DARKPURPLE = '\033[35m'
    GREY = '\033[90m'
    BLUE = '\033[34m'
    DEATH = '\033[91m'
    ALLIANCE = '\033[96m'
    DISBAND = '\033[36m'
    INFO = '\033[93m'


class CmdSigaller:
    pass
    def __init__(self):
        self.event_log = []
        self.standings_log = []


    def capture_to_string(self, func, *args, **kwargs):
        buffer = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = buffer
        try:
            func(*args, **kwargs)
        finally:
            sys.stdout = original_stdout
        return buffer.getvalue()

    def log_event(self, msg, type="event"):
        #Fills stuff on the events page
        if type == "event":
            self.event_log.append(msg)
        #Fills stuff on the standings page
        elif type == "standings":
            self.standings_log.append(msg)


    def event_handler(self, players, side1, side2, source, tag):
        pass
        if len(players) == 1:
            self.log_event(tag + choice(source.ONE_PERSON).format(p=CmdSigaller.get_name_string(players)),type="event")
        else:  # inserted
            if players and (not side2 or randint(0, len(players)) < 3):
                self.log_event(tag * len(players) + choice(source.ONE_GROUP).format(g=CmdSigaller.get_name_string(players)),type="event")
            else:  # inserted
                plural = 's' if len(side1) == 1 else ''
                self.log_event(tag + choice(source.TWO_GROUP).format(g1=CmdSigaller.get_name_string(side1), g2=CmdSigaller.get_name_string(side2), s=plural),type="event")

    def start(self):
        pass
        self.log_event(CmdSigaller.colour(standMsg.WELCOME, bc.PURPLE), CmdSigaller.colour(standMsg.CREDIT, bc.GREY),type="event")
        self.log_event(standMsg.INSTRUCTIONS,type="event")

    def ruleset(self):
        self.log_event(standMsg.RULESET,type="event")

    def lives(self, players):
        self.log_event(standMsg.STARTING_BANNER)
        for player in players:
            self.log_event(standMsg.STARTING.format(p=CmdSigaller.get_name_string([player]), n=player.get_lives()),type="standings")

    def time_change(self, player, n):
        change = ""
        color = bc.GREY
        if n > 0:
            change = 'lost'
            color = bc.RED
        else:
            change = "gained"
            color = bc.GREEN
            n=n*-1
        self.log_event(CmdSigaller.colour(standMsg.TIME_CHANGE.format(p=CmdSigaller.get_name_string([player]),diff=change, n=int(n*60)),color),type="event")

    def timesStanding(self, players, alliances, i):
        self.standings_log = []
        def print_player_time(player):
            player_hours = int(player.get_time())
            self.log_event('\t{name}: {hours}:{min}0'.format(name=CmdSigaller.get_name_string([player]), hours=player_hours,min=int((player.get_time()-player_hours)*6)),type="standings")
        self.log_event(standMsg.STANDINGS.format(num=i),type='standings')
        player_set = set(players)
        first = True
        for alliance in alliances:
            if not first:
                print()
            first = False
            self.log_event(CmdSigaller.colour(alliance.get_name(), bc.ALLIANCE),type="standings")
            alliance.get_members().sort(key=lambda p: p.get_time(), reverse=True)
            for member in alliance.get_members():
                print_player_time(member)
            player_set -= set(alliance.get_members())
        if len(player_set) > 0:
            if len(player_set) < len(players):
                self.log_event(CmdSigaller.colour('\nNo Alliance', bc.ALLIANCE),type="standings")
            player_set = list(player_set)
            player_set.sort(key=lambda p: p.get_time(), reverse=True)
            for player in player_set:
                print_player_time(player)

    def soulbounds(self, players, i):
        self.standings_log = []
        self.log_event(standMsg.STANDINGS.format(num=i),type="standings")
        self.log_event(standMsg.SOULBOUNDS_BANNER,type="standings")
        seen = set()
        for player in players:
            soulmate = player.get_soulbound()
            if soulmate not in seen and player not in seen:
                self.log_event(standMsg.SOULBOUNDS.format(
                    p1=CmdSigaller.get_name_string([player]),
                    p2=CmdSigaller.get_name_string([soulmate]),
                    n=player.get_lives()
                ),type='standings')
                seen.add(player)
                seen.add(soulmate)

    def boogey_pick(self, player):
        self.log_event(standMsg.BOOGEY_PICK.format(p=CmdSigaller.get_name_string([player])),type="event")

    def boogey_cure(self, player):
        self.log_event(standMsg.BOOGEY_CURE.format(p=CmdSigaller.get_name_string([player])),type="event")

    def boogey_fail(self, player):
        self.log_event(standMsg.BOOGEY_FAIL.format(p=CmdSigaller.get_name_string([player])),type="event")

    def boogey_end_fail(self, player):
        self.log_event(standMsg.BOOGEY_END_FAIL.format(p=CmdSigaller.get_name_string([player])),type="event")

    def life_trade(self, player1, player2):
        self.log_event(CmdSigaller.colour(standMsg.TRADE_LIFE.format(p1=CmdSigaller.get_name_string([player1]), p2=CmdSigaller.get_name_string([player2])), bc.GREEN),type="event")

    def alliance_war(self, alliance1, alliance2):
        self.log_event(standMsg.ALLIANCE_FIGHT.format(a1=CmdSigaller.colour(alliance1, bc.ALLIANCE), a2=CmdSigaller.colour(alliance2, bc.ALLIANCE)),type="event")

    def life_gain(self, player):
        self.log_event(CmdSigaller.colour(standMsg.LIFE_GAIN.format(p=CmdSigaller.get_name_string([player])), bc.GREEN),type="event")

    def alliance_create(self, members):
        pass
        if len(allyName.FIRST) == 0 or len(allyName.SECOND) == 0:
            return None
        first, second = (choice(allyName.FIRST), choice(allyName.SECOND))
        allyName.FIRST.remove(first)
        allyName.SECOND.remove(second)
        name = first + ' ' + second
        self.log_event(CmdSigaller.colour(standMsg.ALLIANCE, bc.ALLIANCE).format(players=CmdSigaller.get_name_string(members), n=CmdSigaller.colour(f'({name})', bc.ALLIANCE)),type="event")
        return name

    def alliance_disband(self, alliance):
        pass
        self.log_event(CmdSigaller.colour(standMsg.ALLIANCE_DISBAND.format(alliance=alliance), bc.DISBAND),type="event")

    def alliance_join(self, player, alliance):
        pass
        self.log_event(CmdSigaller.colour(standMsg.ALLIANCE_JOIN, bc.ALLIANCE).format(p=CmdSigaller.get_name_string([player]), alliance=CmdSigaller.colour(alliance, bc.ALLIANCE)),type="event")

    def alliance_leave(self, player, alliance):
        pass
        self.log_event(standMsg.ALLIANCE_LEAVE.format(p=CmdSigaller.get_name_string([player]), alliance=CmdSigaller.colour(alliance, bc.ALLIANCE)),type="event")

    def alliance_kick(self, player, alliance):
        pass
        self.log_event(standMsg.ALLIANCE_KICK.format(p=CmdSigaller.get_name_string([player]), alliance=CmdSigaller.colour(alliance, bc.ALLIANCE)),type="event")

    def event(self, side1, side2, type_of_event):
        pass
        event_set = None
        match type_of_event:
            case 'mp':
                event_set = majPos
            case 'mn':
                event_set = majNeg
            case 'ip':
                event_set = minPos
            case 'in':
                event_set = minNeg
        self.event_handler([], side1, side2, event_set, '')

    def event_alliance(self, group, alliance, type_of_event):
        pass
        event_set = None
        match type_of_event:
            case 'mp':
                event_set = allyInt.MAJPOS
            case 'mn':
                event_set = allyInt.MAJNEG
            case 'ip':
                event_set = allyInt.MINPOS
            case 'in':
                event_set = allyInt.MINNEG

        plural1 = 's' if len(group) == 1 else ''
        plural2 = '' if alliance[-1] == 's' else 's'
        self.log_event(choice(event_set).format(
            g=CmdSigaller.get_name_string(group),
            ally=CmdSigaller.colour(alliance, bc.ALLIANCE),
            s=plural1,
            s2=plural2
        ),type="event")

    def event_deadloot(self, player, dead):
        pass
        plural = 's' if len(player) == 1 else ''
        self.log_event(standMsg.DEADLOOT.format(p=CmdSigaller.get_name_string(player), d=CmdSigaller.get_name_string([dead]), s=plural),type="event")

    def filler(self, players, side1, side2, sesh):
        pass
        if sesh < 3:
            self.event_handler(players, side1, side2, fillEarly, '')
        else:  # inserted
            self.event_handler(players, side1, side2, filler, '')

    def game_next_sesh(self, i):
        pass
        self.log_event(CmdSigaller.colour(standMsg.SESSION_HEADER.format(num=i), bc.INFO),type="event")

    def player_death(self, players):
        pass
        soulbound = players[0].get_soulbound()
        self.event_handler(players, players, [], playerDeath, CmdSigaller.colour('[-] ', bc.DEATH))
        if soulbound!= None:
            for player in players:
                self.log_event(standMsg.SOULMATE_DEATH.format(p=CmdSigaller.get_name_string([player.get_soulbound()])),type="event")

    def player_eliminated(self, player):
        pass
        self.log_event(CmdSigaller.colour(standMsg.ELIMINATION, bc.DEATH).format(p=player.get_name()),type="event")

    def time_elimination(self, player):
        pass
        self.log_event(CmdSigaller.colour(standMsg.TIME_ELIMINATION, bc.DEATH).format(p=player.get_name()),type="event")

    def player_escape(self, player, attackers, attacker_win):
        pass
        msg = playerKill.ATTACKER_ESCAPES
        if attacker_win:
            msg = playerKill.DEFENDER_ESCAPES
        plural = 's' if len(attackers) > 1 else ''
        self.log_event(choice(msg).format(p=CmdSigaller.get_name_string([player]), s=plural, s2='s'.replace(plural, ''), a=CmdSigaller.get_name_string([choice(attackers)])),type="event")

    def player_fight(self, side1, side2):
        pass
        plural = 's' if len(side1) == 1 else ''
        self.log_event(standMsg.FIGHT.format(g1=CmdSigaller.get_name_string(side1), g2=CmdSigaller.get_name_string(side2), s=plural))

    def player_killed(self, player, attacker):
        pass
        self.log_event(CmdSigaller.colour('[-]', bc.DEATH) + choice(playerKill.KILLS).format(p1=CmdSigaller.get_name_string([player]), p2=CmdSigaller.get_name_string([attacker])),type="event")
        if player.get_soulbound()!= None:
            self.log_event(standMsg.SOULMATE_DEATH.format(p=CmdSigaller.get_name_string([player.get_soulbound()])),type="event")

    def player_red(self, player):
        pass
        self.log_event(CmdSigaller.colour(standMsg.RED, bc.RED).format(p=CmdSigaller.get_name_string([player])),type="event")

    def player_yellow(self, player):
        pass
        self.log_event(CmdSigaller.colour(standMsg.YELLOW, bc.YELLOW).format(p=CmdSigaller.get_name_string([player])),type="event")

    def player_trap(self, template, player, target, kill):
        pass
        plural, plural2 = ('s', 'was') if len(target) == 1 else ('', 'were')
        col, tag, template = (bc.DEATH, template[:4], template[4:]) if kill else (bc.BLUE, '', template)
        self.log_event(CmdSigaller.colour(tag * len(target) + template, col).format(p=CmdSigaller.get_name_string([player]), w=plural2, s=plural, p2=CmdSigaller.get_name_string(target)),type="event")

    def stats(self, players, alliances, i):
        pass
        self.standings_log = []  #clear log at the start
        def print_player(player):
            self.log_event('\t{name}: {lives}'.format(name=CmdSigaller.get_name_string([player]), lives=player.get_lives()),type="standings")
        self.log_event(standMsg.STANDINGS.format(num=i),type="standings")
        player_set = set(players)
        first = True
        for alliance in alliances:
            if not first:
                print()
            first = False
            self.log_event(CmdSigaller.colour(alliance.get_name(), bc.ALLIANCE),type="standings")
            alliance.get_members().sort(key=lambda p: p.get_lives(), reverse=True)
            for member in alliance.get_members():
                print_player(member)
            player_set -= set(alliance.get_members())
        if len(player_set) > 0:
            if len(player_set) < len(players):
                self.log_event(CmdSigaller.colour('\nNo Alliance', bc.ALLIANCE),type="standings")
            player_set = list(player_set)
            player_set.sort(key=lambda p: p.get_lives(), reverse=True)
            for player in player_set:
                print_player(player)

    def stats_end(self, players, eliminated):
        pass
        self.log_event(standMsg.FINAL_STANDINGS,type="standings")
        all_players = players + eliminated
        for i, player in enumerate(all_players, start=1):
            plural = '' if player.get_kills() == 1 else 's'
            self.log_event(standMsg.RANK.format(num=i, p=player.get_name(), kills=CmdSigaller.colour(f'({player.get_kills()} kill{plural})', bc.GREY), deaths=CmdSigaller.colour(f' ({player.get_deaths()} death{plural})',bc.GREY)),type="standings")

    def stats_win(self, player):
        pass
        self.log_event(standMsg.WINNER.format(p=CmdSigaller.colour(player.get_name(), bc.PURPLE)),type="standings")

    def cont(self):
        pass

    @staticmethod
    def get_name_string(players):
        pass
        if len(players) == 0:
            return ''
        if len(players) == 1:
            return CmdSigaller.get_name_colour(players[0])

        def combine(x, y):
            return x + ', ' + y
        player_string = map(lambda x: CmdSigaller.get_name_colour(x), players[:(-1)])
        return reduce(combine, player_string) + ' and ' + CmdSigaller.get_name_colour(players[(-1)])

    @staticmethod
    def get_name_colour(player):
        pass
        player_string = player.get_name() + bc.ENDC
        col = ''
        if player.is_boogey():
            col = bc.PURPLE
            return col + player_string
        lives = player.get_lives()
        match lives:
            case 0:
                col = bc.GREY
            case 1:
                col = bc.RED
            case 2:
                col = bc.YELLOW
            case 3:
                col = bc.GREEN
            case _:
                col = bc.DARKGREEN
        return col + player_string

    @staticmethod
    def colour(string, colour):
        pass
        return colour + string + bc.ENDC
sig = CmdSigaller()