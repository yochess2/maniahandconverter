from django.conf import settings
from django.core.files.storage import default_storage

from .converters import create_hh_object, parse_hh_json
from .models import HH, Player, Game, HH_Player, HH_Player_Game, Hand, Hand_Player, HHJson
from .forms import HHForm

import boto3
import time, json
#dict_keys(['players', 'games', 'unconvertable_hands', 'hands'])

def handle_hh_models(hh, hh_obj):
    games = {}
    players = {}

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

    # for h in hh_obj['hands']:
    #     v = h['details']
    #     hand = Hand(
    #         game        = games[v['game']],
    #         hand_number = v['hand_number'],
    #         date_played = v['date'],
    #         time_played = v['time'],
    #         sb          = v['sb'],
    #         bb          = v['bb'],
    #         ante        = v['ante'],
    #         table       = v['table'],
    #         blind_type  = v['blind_type'],
    #         rake        = v['rake'],
    #         pot         = v['pot'],
    #         sitting     = v['sitting'],
    #         dealt       = v['dealt'],
    #         body        = v['body'],
    #     )
    #     hand.save()

    #     for p in v['players']:
    #         hh_player = Hand_Player(
    #             hand    = hand,
    #             player  = players[p],
    #             amount  = v['players'][p]['result'],
    #             sitting = v['players'][p]['is_sitting']
    #         )
    #         hh_player.save()

    # d = time.time()
    # print('next database time:', d - c)

def save_json_file(hh, hh_obj):
    file = default_storage.open(hh.file.name, 'w')
    json_text = json.dumps(hh_obj)
    file.write(json_text)
    hh_json = HHJson(hh=hh, file=file)
    hh_json.save()
    return hh_json

def save_hh_file(self, request, csrf, data):
    hhForm = HHForm(self.request.POST, self.request.FILES)
    if hhForm.is_valid() == True:
        a = time.time()
        hh = hhForm.save()
        b = time.time()
        print('post1: ', b - a)
        data['is_valid'] = True
        data['hh_id'] = hh.id
        data['csrf'] = csrf

def save_hh_obj(self, request, csrf, hh_id, data):
    hh = HH.objects.get(id=hh_id)
    a = time.time()
    hh_obj = create_hh_object(hh)
    b = time.time()
    print('post2a: ', b - a)
    hh_json = save_json_file(hh, hh_obj)
    c = time.time()
    print('post2b: ', c - b)
    data['is_valid'] = True
    data['csrf'] = csrf
    data['hh_json_id'] = hh_json.id

def save_hh_models(self, request, csrf, hh_json_id, data):
    hh_json = HHJson.objects.get(id=hh_json_id)
    a = time.time()
    hh_obj = parse_hh_json(hh_json.file)
    handle_hh_models(hh_json.hh, hh_obj)
    b = time.time()
    print('post3: ', b - a)
    data['is_valid'] = True
    data['csrf'] = csrf
    data['players'] = hh_obj['players']

def post4(self, request, csrf, hero, data):
    data['is_valid'] = True
    data['hero'] = hero
