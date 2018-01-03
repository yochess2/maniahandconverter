from .models import HH, Player, Game, HH_Player, HH_Player_Game
import time
#dict_keys(['players', 'games', 'unconvertable_hands', 'hands'])

def file_upload_post(hh, hh_obj):
    games = {}
    players = {}
    a = time.time()
    hh.save()
    b = time.time()
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

    print('database time: ', time.time() - b)

