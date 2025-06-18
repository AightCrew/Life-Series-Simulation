# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: C:\Users\yuyan\Documents\life-series-simulator\gameMessages\trapTypes.py
# Bytecode version: 3.10.0rc2 (3439)
# Source timestamp: 2023-09-04 04:04:31 UTC (1693800271)

MINECART = {'set': '[~] {p} sets a TNT minecart on a powered rail...', 'disarm': "[=] {p2} break{s} {p}'s TNT minecart.", 'escape': "[=] {p2} trigger{s} {p}'s TNT minecart, but survive{s} the explosion.", 'kill': "[-] {p2} {w} blown up by {p}'s TNT minecart trap"}
FALL = {'set': '[~] {p} digs a deep pit in the ground...', 'disarm': '[=] {p2} cover{s} the hole left by {p}.', 'escape': "[=] {p2} fall{s} into {p}'s trap, but survive{s}.", 'kill': "[-] {p2} fell from a high place, thanks to {p}'s trap"}
LAVA = {'set': '[~] {p} puts down a few buckets of lava...', 'disarm': "[=] {p2} block{s} up {p}'s lava.", 'escape': "[=] {p2} fall{s} into {p}'s lava, but escape{s} and puts themselves out.", 'kill': "[-] {p2} tried to swim in {p}'s lava trap"}
SKULK = {'set': '[~] {p} links a skulk sensor to a pile of TNT...', 'disarm': "[=] {p2} break{s} {p}'s sensor.", 'escape': "[=] {p2} trigger{s} {p}'s sensor, but survive{s} the explosion.", 'kill': "[-] {p2} {w} blown up by {p}'s skulk sensor trap"}
OBSERVER = {'set': '[~] {p} links an observer to a powered rail...', 'disarm': "[=] {p2} dig{s} around until they find and break {p}'s observer.", 'escape': "[=] {p2} trigger{s} {p}'s observer, but survive{s} the explosion.", 'kill': "[-] {p2} {w} blown up by {p}'s observer trap"}
DOOR = {'set': '[~] {p} carefully pushes a TNT minecart onto a closed door...', 'disarm': "[=] {p2} break{s} {p}'s TNT minecart.", 'escape': "[=] {p2} trigger{s} {p}'s TNT minecart, but survive{s} the explosion.", 'kill': "[-] {p2} {w} blown up by {p}'s trapped door"}
CHEST = {'set': '[~] {p} places down a trapped chest...', 'disarm': "[=] {p2} break{s} the TNT linked to {p}'s chest.", 'escape': "[=] {p2} open{s} {p}'s trapped chest, but survive{s} the explosion.", 'kill': "[-] {p2} {w} blown up by {p}'s trapped chest"}
BARREL = {'set': '[~] {p} places a barrel on top of an observer...', 'disarm': "[=] {p2} break{s} the observer linked to {p}'s barrel.", 'escape': "[=] {p2} open{s} {p}'s trapped barrel, but survive{s} the explosion.", 'kill': "[-] {p2} {w} blown up by {p}'s trapped barrel"}
BLOCK = {'set': '[~] {p} places a block on top of an observer...', 'disarm': "[=] {p2} break{s} the observer linked to {p}'s block.", 'escape': "[=] {p2} break{s} {p}'s trapped block, but survive{s} the explosion.", 'kill': "[-] {p2} {w} blown up by {p}'s trapped block"}
STALAGMITE = {'set': '[~] {p} places dripstone on a block...', 'disarm': "[=] {p2} break{s} {p}'s dripstone.", 'escape': "[=] {p2} fall{s} on {p}'s dripstone, but survive{s}.", 'kill': '[-] {p2} {w} impaled on a stalagmite, thanks to {p}'}
TYPES = [MINECART, FALL, LAVA, SKULK, OBSERVER, DOOR, CHEST, BARREL, BLOCK, STALAGMITE]