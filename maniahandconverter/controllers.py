from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404

from .converter import hh_to_object
from .converters import create_new_hh_text, create_hh_details
from .models import (
    HH,
    Player,
    Game,
    HHJson_Player,
    HHJson_Player_Game,
    HHJson,
    HHNew
)

import json, boto3, uuid, magic

HH_LOCATION = settings.AWS_HH_LOCATION
S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
S3_DOMAIN = settings.AWS_S3_CUSTOM_DOMAIN

def handle_get_hh(hh_json_id, user):
    if not bool(hh_json_id):
        return {'is_valid':False, 'message':'Invalid Operation'}
    hh_json = get_object_or_404(HHJson, id=hh_json_id)
    get_object_or_404(HH, id=hh_json.hh.id,user=user)
    return get_hh_text_from_s3(hh_json.hh.path)

def handle_get_new_hh(new_hh_id,user):
    if not bool(new_hh_id):
        return {'is_valid':False, 'message':'Invalid Operation'}
    new_hh = get_object_or_404(HHNew, id=new_hh_id)
    get_object_or_404(HH, id=new_hh.hh_json.hh.id,user=user)
    new_hh = HHNew.objects.get(id=new_hh_id)
    return new_hh.file.read()

def handle_get_hh_obj(hh_json_id,user):
    if not bool(hh_json_id):
        return {'is_valid':False, 'message':'Invalid Operation'}
    hh_json = get_object_or_404(HHJson, id=hh_json_id)
    get_object_or_404(HH, id=hh_json.hh.id,user=user)
    hh_obj = parse_hh_json(hh_json.file)
    return create_hh_details(hh_obj)

def handle_create_new_hh(hero_id,user):
    if not bool(hero_id):
        return {'is_valid':False, 'message':'Invalid Operation'}
    hh_json_player = get_object_or_404(HHJson_Player, id=hero_id)
    hero = hh_json_player.player.name
    hh_json = hh_json_player.hh_json
    get_object_or_404(HH, id=hh_json.hh.id,user=user)

    if HHNew.objects.filter(hero=hero, hh_json=hh_json).exists():
        return { 'is_valid': False }
    else:
        return handle_create_more_new_hh(hh_json.id, hero,user)

def handle_delete(hh_json_id,user):
    if not bool(hh_json_id):
        return {'is_valid':False, 'message':'Invalid Operation'}
    hh_json = get_object_or_404(HHJson, id=hh_json_id)
    get_object_or_404(HH, id=hh_json.hh.id,user=user)
    hh_json.hh.active = False
    hh_json.hh.save()
    return {
        'is_valid': True
    }

def handle_sign_s3(file_name, file_type, file_size, ext, user):
    if ext != '.txt':
        return {'is_valid': False,'message': 'Not a .txt file'}

    if int(file_size) > 1999000:
        return {'is_valid': False, 'message': 'File must be under 2MB'}

    hh              = create_hh_model(file_name, file_type, file_size, ext, user)
    presigned_post  = create_s3_signature(hh.path, file_type)
    return {
        'is_valid': True,
        'data': presigned_post,
        'hh_id': hh.id,
        'url': '{}/{}'.format(S3_DOMAIN, hh.path)
    }

def handle_create_hh_json(hh_id, key, user):
    if not bool(hh_id) or not bool(key):
        return {'is_valid':False, 'message':'Invalid Operation'}

    hh      = update_hh_model(hh_id, user)
    hh_text = get_hh_text_from_s3(key)

    if hh_text == '':
        return {'is_valid':False, 'message': 'You trying to hack me?'}

    hh_obj  = hh_to_object.init(hh_text)
    hh_json = create_hh_json_model(hh_obj, hh, user)
    return {
        'is_valid': True,
        'hh_json_id': hh_json.id,
    }

def handle_create_all_models(hh_json_id,user):
    if not bool(hh_json_id):
        return {'is_valid':False, 'message':'Invalid Operation'}
    hh_json = get_object_or_404(HHJson,id=hh_json_id)
    get_object_or_404(HH,id=hh_json.hh.id,user=user)
    hh_obj  = parse_hh_json(hh_json.file)
    create_rest_of_models(hh_json, hh_obj)
    return {
        'is_valid': True,
        'players': hh_obj['players']
    }

def handle_create_more_new_hh(hh_json_id, hero, user):
    if not bool(hh_json_id) or not bool(hero):
        return {'is_valid':False, 'message':'Invalid Operation'}
    hh_json = get_object_or_404(HHJson, id=hh_json_id)
    get_object_or_404(HH, id=hh_json.hh.id, user=user)
    new_hh = create_new_hh_model(hh_json, hero, user)
    return {
        'is_valid': True,
        'hero': hero,
        'new_hh_id': new_hh.id
    }

#############################
##### S3 HELPER METHODS #####
#############################

def create_s3_signature(hh_path, file_type):
    s3 = boto3.client('s3')
    return s3.generate_presigned_post(
        Bucket = S3_BUCKET,
        Key = hh_path,
        Fields = {"acl": "private", "Content-Type": file_type},
        Conditions = [
            {"acl": "private"},
            {"Content-Type": file_type}
        ],
        ExpiresIn = 3600
    )

def get_hh_text_from_s3(key):
    s3 = boto3.resource('s3')
    hh_s3 = s3.Object(S3_BUCKET, key)
    text = hh_s3.get()['Body'].read()

    if magic.from_buffer(text,mime=True) != 'text/plain':
        return ''

    hh_text = text.decode('utf-8', 'ignore')
    return hh_text

################################
##### Model HELPER METHODS #####
################################

# hh.path is (:path)/(:id).txt
def create_hh_model(file_name, file_type, file_size, ext, user):
    hh = HH.active_items.create(name=file_name, file_type=file_type, size=file_size, user=user)
    hh.save()
    hh.path = "{}/{}/{}".format(HH_LOCATION, user, str(uuid.uuid1()), ext)
    hh.save()
    return hh

def update_hh_model(hh_id,user):
    hh = get_object_or_404(HH, id=hh_id,user=user)
    hh.uploaded = True
    hh.save()
    return hh

def create_hh_json_model(hh_obj, hh, user):
    json_text = json.dumps(hh_obj)
    file_name = "{}/{}.txt".format(user,str(uuid.uuid1()))

    file = default_storage.open(file_name, 'w')
    file.write(json_text)

    hh_json = HHJson(hh=hh, file=file)
    hh_json.save()
    return hh_json

def create_rest_of_models(hh_json, hh_obj):
    hh = hh_json.hh
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
        hh_json_player = HHJson_Player(hh_json=hh_json, player=players[p])
        hh_json_player.save()

        for g in hh_obj['players'][p]['games']:
            amount = hh_obj['players'][p]['games'][g]['amount']
            count = hh_obj['players'][p]['games'][g]['count']
            sit = hh_obj['players'][p]['games'][g]['sit']
            hh_json_player_game = HHJson_Player_Game(
                hh_json_player=hh_json_player,
                game=games[g],
                amount=amount,
                count=count,
                sit=sit
            )
            hh_json_player_game.save()

def create_new_hh_model(hh_json, hero,user):
    hh_obj = parse_hh_json(hh_json.file)
    new_hh_text = create_new_hh_text(hh_obj, hero)
    file_name = "{}/{}.txt".format(user, str(uuid.uuid1()))

    file = default_storage.open(file_name, 'w')
    file.write(new_hh_text)

    new_hh = HHNew(hh_json=hh_json, file=file, hero=hero)
    new_hh.save()
    return new_hh

################################
##### Other HELPER METHODS #####
################################

def parse_hh_json(file):
    byte_text = file.read()
    string = byte_text.decode('utf-8')
    hh_obj = json.loads(string)
    return hh_obj
