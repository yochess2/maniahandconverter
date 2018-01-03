from django.core.files.storage import default_storage
from .models import HH, Player, Game, HH_Player, HH_Player_Game, Hand, Hand_Player
import time, json
#dict_keys(['players', 'games', 'unconvertable_hands', 'hands'])

def create_hh(hh, hh_obj):
    games = {}
    players = {}

    a = time.time() #1

    hh.save()

    b = time.time() #2
    print('upload time: ', b - a)

    for g in hh_obj['games']:
        game, created = Game.objects.get_or_create(name=g)
        game.save()
        if game.name not in games:
            games[game.name] = game

    for p in hh_obj['players']:
        player, created = Player.objects.get_or_create(name=p)
        player.save()
        if player.name not in players:
            players[player.name] = player

    for p in players:
        hh_player = HH_Player(hh=hh, player=players[p])
        hh_player.save()

        for g in hh_obj['players'][p]['games']:
            amount = hh_obj['players'][p]['games'][g]['amount']
            count = hh_obj['players'][p]['games'][g]['count']
            sit = hh_obj['players'][p]['games'][g]['sit']
            hh_player_game = HH_Player_Game(hh_player=hh_player,game=games[g],amount=amount,count=count,sit=sit)
            hh_player_game.save()

    c = time.time()
    print('first database time: ', c - b)

    for h in hh_obj['hands']:
        v = h['details']
        hand = Hand(
            game        = games[v['game']],
            hand_number = v['hand_number'],
            date_played = v['date'],
            time_played = v['time'],
            sb          = v['sb'],
            bb          = v['bb'],
            ante        = v['ante'],
            table       = v['table'],
            blind_type  = v['blind_type'],
            rake        = v['rake'],
            pot         = v['pot'],
            sitting     = v['sitting'],
            dealt       = v['dealt'],
            body        = v['body'],
        )
        hand.save()

        for p in v['players']:
            hh_player = Hand_Player(
                hand    = hand,
                player  = players[p],
                amount  = v['players'][p]['result'],
                sitting = v['players'][p]['is_sitting']
            )
            hh_player.save()

    d = time.time()
    print('next database time:', d - c)

def create_json_file(hh, hh_obj):
    json_file = default_storage.open(hh.file.name, 'w')

    file_text = json.dumps(hh_obj)
    json_file.write(file_text)

    hh_json = HHJson(hh=hh, file=json_file)
    hh_json.save()
