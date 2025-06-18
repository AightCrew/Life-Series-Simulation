from random import shuffle,randint
from flask import Flask, render_template, request, redirect, url_for, session
from markupsafe import Markup
from lifesim.playerManagement import Alliance
import uuid

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for session to work

# Store per-session games
games = {}
session_data_store = {}

from lifesim.lifesim__main__ import Game
from lifesim.rulesets import ThirdLife, LastLife, DoubleLife, LimitedLife
from lifesim.signallers import sig, ansi_to_html


@app.before_request
def assign_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@app.route('/', methods=['GET', 'POST'])
def index():
    session_id = session['session_id']

    if request.method == 'POST':
        # Store input in the session
        session['players'] = request.form.get('players', '')
        session['ruleset'] = request.form.get('ruleset', 'tl')
        session['lives'] = request.form.get('lives', '3')
        session['boogey'] = request.form.get('boogey', 'yes')
        session['lifesteal'] = request.form.get('lifesteal', 'no')

        players = [p.strip() for p in session['players'].split(',') if p.strip()]
        lives = int(session['lives'])
        boogey = (session['boogey'] == 'no')
        lifesteal = (session['lifesteal'] == 'yes')

        # Create game and session data
        game = Game()
        games[session_id] = game
        session_data_store[session_id] = {'log': {}, 'standings': {}, 'session': 0}
        sig.log = []

        rulesets = {
            'tl': ThirdLife,
            'll': LastLife,
            'dl': DoubleLife,
            'lil': LimitedLife
        }
        randNum = randint(1,7)
        while randNum>0:
            shuffle(players)
            randNum-=1
        RuleClass = rulesets.get(session['ruleset'])
        if not RuleClass:
            return "Invalid ruleset"

        rule = RuleClass(game, lives, boogey, lifesteal)
        game.set_rules(rule)

        for p in players:
            game.add_player(p)

        game.init()
        return redirect(url_for('show_start'))

    #Check if player already input something in a previous session
    return render_template(
        'index.html',
        last_players=session.get('players', ''),
        last_ruleset=session.get('ruleset', 'tl'),
        last_lives=session.get('lives', '3'),
        last_boogey=session.get('boogey', 'yes'),
        last_lifesteal=session.get('lifesteal', 'no')
    )


@app.route('/play')
def play():
    session_id = session['session_id']
    game = games.get(session_id)
    session_data = session_data_store.get(session_id)

    if not game or not session_data:
        return redirect(url_for('index'))

    sig.event_log = []
    sig.standings_log = []

    if len(game.players) <= 1:
        # Game over
        winner = game.players[0] if game.players else game.eliminated[0]
        all_players = game.players + game.eliminated
        stats = [{
            'rank': i,
            'name': p.get_name(),
            'kills': p.get_kills(),
            'deaths': p.get_deaths()
        } for i, p in enumerate(all_players, start=1)]
        return render_template('game_over.html', winner=winner.get_name(), stats=stats)

    session_num = game.session + 1
    game.run_day()
    session_data['session'] = session_num

    session_data['log'][session_num] = [
        Markup(ansi_to_html(line)) for line in sig.event_log
    ]
    sig.event_log = []

    # Standings
    if isinstance(game.rule, LimitedLife):
        sig.timesStanding(game.players, game.alliances, session_num)
    elif isinstance(game.rule, DoubleLife):
        sig.soulbounds(game.players, session_num)
    else:
        sig.stats(game.players, game.alliances, session_num)

    session_data['standings'][session_num] = [
        Markup(ansi_to_html(line)) for line in sig.standings_log
    ]
    sig.standings_log = []
    print("Alliance state:", game.alliances)
    print("Sig ID:", id(sig))
    print("Rule object:", repr(game.rule))
    return redirect(url_for('show_session', n=session_num))


@app.route('/start')
def show_start():
    session_id = session['session_id']
    game = games.get(session_id)
    if not game:
        return redirect(url_for('index'))

    sig.standings_log = []

    if isinstance(game.rule, LimitedLife):
        sig.timesStanding(game.players, game.alliances, 0)
    elif isinstance(game.rule, DoubleLife):
        sig.soulbounds(game.players, 0)
    else:
        sig.lives(game.players)

    initial_lives = [Markup(ansi_to_html(line)) for line in sig.standings_log]
    sig.standings_log = []

    return render_template("start.html", lives=initial_lives)





@app.route('/session/<int:n>')
def show_session(n):
    session_id = session['session_id']
    session_data = session_data_store.get(session_id)
    if not session_data:
        return redirect(url_for('index'))

    log = session_data['log'].get(n, [])
    return render_template('session.html', session=n, log=log)


@app.route('/standings/<int:n>')
def show_standings(n):
    session_id = session['session_id']
    session_data = session_data_store.get(session_id)
    if not session_data:
        return redirect(url_for('index'))

    raw_lines = session_data['standings'].get(n, [])

    standings = []
    current_group = None

    for line in raw_lines:
        stripped = line.strip()

        # Skip the session header
        if "-- SESSION" in stripped:
            continue

        # Group header: lines with cyan span and no colon
        if 'color:cyan' in stripped:
            if current_group:
                standings.append(current_group)
            current_group = {"group": stripped, "players": []}

        # Player line
        elif ":" in stripped and current_group:
            current_group["players"].append(stripped)

    if current_group:
        standings.append(current_group)

    print("Standings: ", standings)

    return render_template('standings.html', session=n, standings=standings)

@app.route('/set_alliance', methods=['GET', 'POST'])
def set_alliance():
    session_id = session['session_id']

    if request.method == 'POST':
        # Save inputs into the session
        session['set_ruleset'] = request.form.get('ruleset', 'tl')
        session['set_lives'] = request.form.get('lives', '3')
        session['set_boogey'] = request.form.get('boogey', 'yes')
        session['set_lifesteal'] = request.form.get('lifesteal', 'no')
        session['set_unallied'] = request.form.get('unallied', '')

        # Save all group names and members
        session['set_group_names'] = request.form.getlist('group_name')
        session['set_group_members'] = request.form.getlist('group_members')

        # Combine players
        group_names = session['set_group_names']
        group_members_raw = session['set_group_members']
        unallied_players = [p.strip() for p in session['set_unallied'].split(',') if p.strip()]

        groups = []
        all_group_players = set()
        for name, members_str in zip(group_names, group_members_raw):
            members = [p.strip() for p in members_str.split(',') if p.strip()]
            all_group_players.update(members)
            groups.append((name, members))

        players = sorted(set(unallied_players) | all_group_players)

        # Validate soulmates
        if session['set_ruleset'] == 'dl' and any(len(pair) != 2 for _, pair in groups):
            return "Each soulmate pair must contain exactly 2 players.", 400

        # Build game
        game = Game()
        games[session_id] = game
        session_data_store[session_id] = {'log': {}, 'standings': {}, 'session': 0}
        sig.log = []

        rulesets = {
            'tl': ThirdLife,
            'll': LastLife,
            'dl': DoubleLife,
            'lil': LimitedLife
        }
        RuleClass = rulesets.get(session['set_ruleset'])
        if not RuleClass:
            return "Invalid ruleset"

        rule = RuleClass(
            game,
            int(session['set_lives']),
            session['set_boogey'] == 'no',
            session['set_lifesteal'] == 'yes'
        )
        game.set_rules(rule)
        game.set_alliance()

        for p in players:
            game.add_player(p)

        game.init()

        if session['set_ruleset'] == 'dl':
            for _, pair in groups:
                if len(pair) == 2:
                    p1 = game.get_player(pair[0])
                    p2 = game.get_player(pair[1])
                    if p1 and p2:
                        p1.set_soulbound(p2)
                        p2.set_soulbound(p1)
        else:
            for name, members in groups:
                alliance = Alliance(name)
                for pname in members:
                    p = game.get_player(pname)
                    if p:
                        p.set_alliance(alliance)
                game.alliances.append(alliance)

        return redirect(url_for('show_start'))

    # GET: Pre-fill form from session if available
    group_data = zip(
        session.get('set_group_names', ['Group 1']),
        session.get('set_group_members', [''])
    )

    return render_template(
        'set_alliance.html',
        last_ruleset=session.get('set_ruleset', 'tl'),
        last_lives=session.get('set_lives', '3'),
        last_boogey=session.get('set_boogey', 'yes'),
        last_lifesteal=session.get('set_lifesteal', 'no'),
        last_groups=group_data,
        last_unallied=session.get('set_unallied', '')
    )

