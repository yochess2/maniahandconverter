from django.conf import settings
from django.core.files.storage import default_storage

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

import boto3
import time, json, os, boto3

HH_LOCATION = settings.AWS_HH_LOCATION
S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
S3_DOMAIN = settings.AWS_S3_CUSTOM_DOMAIN

def handle_get_hh(hhjson_id):
    hhjson = HHJson.objects.get(id=hhjson_id)
    return get_hh_text_from_s3(hhjson.hh.path)

def handle_get_new_hh(new_hh_id):
    new_hh = HHNew.objects.get(id=new_hh_id)
    return new_hh.file.read()

def handle_get_hh_obj(hhjson_id):
    hhjson = HHJson.objects.get(id=hhjson_id)
    hh_obj = parse_hh_json(hhjson.file)
    return create_hh_details(hh_obj)

def handle_history_detail(hero_id):
    hh_json_player = HHJson_Player.objects.get(id=hero_id)
    hero = hh_json_player.player.name
    hh_json = hh_json_player.hh_json

    if len(HHNew.objects.filter(hero=hero, hh_json=hh_json)) > 0:
        return { 'is_valid': False }
    else:
        return handle_convert(hh_json.id, hero)


def handle_sign_s3(file_name, file_type, file_size, ext):
    if ext != '.txt':
        return {'is_valid': False,'message': 'Not a .txt file'}

    hh              = create_hh_model(file_name, file_type, file_size, ext)
    presigned_post  = create_s3_signature(hh.path, file_type)
    return {
        'is_valid': True,
        'data': presigned_post,
        'hh_id': hh.id,
        'url': '{}/{}'.format(S3_DOMAIN, hh.path)
    }

def handle_fileupload_1(hh_id, key):
    hh      = update_hh_model(hh_id)
    hh_text = get_hh_text_from_s3(key)
    hh_obj  = hh_to_object.init(hh_text)
    hh_json = create_hh_json_model(hh_obj, hh)
    return {
        'is_valid': True,
        'hh_json_id': hh_json.id,
    }

def handle_fileupload_2(hh_json_id):
    hh_json = HHJson.objects.get(id=hh_json_id)
    hh_obj  = parse_hh_json(hh_json.file)
    create_rest_of_models(hh_json, hh_obj)
    return {
        'is_valid': True,
        'players': hh_obj['players']
    }

def handle_convert(hh_json_id, hero):
    hh_json = HHJson.objects.get(id=hh_json_id)
    new_hh = create_new_hh_model(hh_json, hero)
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
    hh_text = hh_s3.get()['Body'].read().decode('utf-8')
    return hh_text

################################
##### Model HELPER METHODS #####
################################

# hh.path is (:path)/(:id).txt
def create_hh_model(file_name, file_type, file_size, ext):
    hh = HH.objects.create(name=file_name, file_type=file_type, size=file_size)
    hh.save()
    hh.path = "{}/{}{}".format(HH_LOCATION, str(hh.id), ext)
    hh.save()
    return hh

def update_hh_model(hh_id):
    hh = HH.objects.get(id=hh_id)
    hh.uploaded = True
    hh.save()
    return hh

def create_hh_json_model(hh_obj, hh):
    json_text = json.dumps(hh_obj)
    file_name = "{}.txt".format(hh.id)

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
            hh_json_player_game = HHJson_Player_Game(hh_json_player=hh_json_player,game=games[g],amount=amount,count=count,sit=sit)
            hh_json_player_game.save()

def create_new_hh_model(hh_json, hero):
    hh_obj = parse_hh_json(hh_json.file)
    new_hh_text = create_new_hh_text(hh_obj, hero)
    file_name = "{}_{}.txt".format(hh_json.hh.id, hero)

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
