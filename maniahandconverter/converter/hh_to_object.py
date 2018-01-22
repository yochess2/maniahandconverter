import re

def init(old_hh_text):
    def delete_weird_char(text):
        if text[0:4] != "Hand" and text[1:5] == "Hand":
            return text[1:]
        if text[0:4] != "Hand" and text[3:7] == "Hand":
            return text[3:]
        return text

    def split_into_hands_text(text):
        return text.replace('\n\n', '\n\r\n').split('\n\r\n')

    def filter_hand_text(text):
        re_filters = {
            'waiting': r'^Seat \d: .* \(\d+\.?\d*\) - waiting for big blind',
            'addon': r'^.* adds \d+\.?\d* chips',
            'chat': r'^.*: ".*"'
        }
        for k in re_filters:
            text = re.sub(re_filters[k], '', text, flags=re.MULTILINE)
        return text

    def strip_empty_lines(hand, body):
        lines = []
        push_to_body = True
        for line in hand.split('\n'):
            stripped_line = line.strip()
            if len(stripped_line) > 0:
                lines.append(stripped_line)
                if stripped_line == "** Summary **":
                    push_to_body = False
                if push_to_body == True:
                    body.append(stripped_line)
        return lines

    hh_obj = {
        'players': {},
        'games': {},
        'unconvertable_hands': [],
        'hands': []
    }

    for old_hand_text in split_into_hands_text(delete_weird_char(old_hh_text)):
        body = []
        old_hand_lines = strip_empty_lines(filter_hand_text(old_hand_text.strip()), body)
        if len(old_hand_lines) == 0:
            continue
        object_hand = create_hand(old_hand_lines, old_hand_text, body)
        if object_hand['error']['value'] == False:
          hh_obj['hands'].append(object_hand)
          get_stats(hh_obj, object_hand['details'])
        else:
          hh_obj['unconvertable_hands'].append(object_hand)

    return hh_obj

def create_hand(old_lines, old_hand_text, body):
    def get_hand_and_date(object_hand, line, regex):
        hand_and_date = re.match(regex, line)
        if bool(hand_and_date) == False:
            object_hand['error']['value'] = True
            object_hand['error']['message'] = 'Invalid Line 1'
            return False
        object_hand['details']['hand_number'] = hand_and_date.group(1)
        object_hand['details']['date'] = hand_and_date.group(2)
        object_hand['details']['time'] = hand_and_date.group(3)
        return True

    def get_game_and_stake(object_hand, line, regex):
        game_and_stake = re.search(regex, line)
        if bool(game_and_stake) == False:
            object_hand['error']['value'] = True
            object_hand['error']['message'] = 'Invalid Line 2'
            return False
        object_hand['details']['game'] = game_and_stake.group(1)
        object_hand['details']['blind_type'] = game_and_stake.group(2)
        object_hand['details']['sb'] = game_and_stake.group(3)
        object_hand['details']['bb'] = game_and_stake.group(4)
        object_hand['details']['ante'] = game_and_stake.group(6) or '0'
        return True

    def verify_mania(object_hand, line, regex):
        site = re.search(regex, line)
        if bool(site) == False:
            object_hand['error']['value'] = True
            object_hand['error']['message'] = 'Invalid Line 3'
        return True

    def get_table(object_hand, line, regex):
        table = re.search(regex, line)
        if bool(table) == False:
            object_hand['error']['value'] = True
            object_hand['error']['message'] = 'Invalid Line 4'
            return False
        object_hand['details']['table'] = table.group(1)
        return True

    def is_not_cancelled(object_hand, line, regex):
        if line == re_lines['cancelled']:
            object_hand['error']['value'] = True
            object_hand['error']['is_cancelled'] = True
            object_hand['error']['message'] = 'Hand is Cancelled'
            return False
        return True

    def get_rake_and_pot(object_hand, old_hand_text, regex):
        rake = re.search(regex, old_hand_text, re.M)
        if bool(rake) == False:
            object_hand['error']['value'] = True
            object_hand['error']['message'] = 'No Rake Found'
            return False
        object_hand['details']['rake'] = rake.group(1)
        object_hand['details']['pot'] = rake.group(2)
        return True

    # 'player_result': r'^Seat \d+: (.*) \(([+|-]\d+\.?\d*)\) \[(.*)\] (.*)',
    def get_players(object_hand, old_hand_text, re_seating, re_result):
        seatings = re.findall(re_seating, old_hand_text, flags=re.M)
        results = re.findall(re_result, old_hand_text, flags=re.M)
        if bool(seatings) == False:
            object_hand['error']['value'] = True
            object_hand['error']['message'] = 'Invalid Player Seatings'
            return False
        if bool(results) == False:
            object_hand['error']['value'] = True
            object_hand['error']['message'] = 'Invalid Player Results'
            return False
        if len(list(filter(lambda p: p[3] == '', seatings))) != len(results):
            object_hand['error']['value'] = True
            object_hand['error']['message'] = 'Missing 1+ Player Summary'
            return False
        players = {}
        for p_tuple in seatings:
            players[p_tuple[1]] = {
                'seat': p_tuple[0],
                'name': p_tuple[1],
                'starting': p_tuple[2],
                'is_sitting': p_tuple[3] != ''
            }
        for p_tuple in results:
            if p_tuple[0] in players == False:
                object_hand['error']['value'] = True
                object_hand['error']['message'] = 'Invalid Player Summary'
                return False
            players[p_tuple[0]]['result'] = p_tuple[1]
            players[p_tuple[0]]['hole'] = p_tuple[2]
            players[p_tuple[0]]['summary'] = p_tuple[3]
        object_hand['details']['sitting'] = 0
        object_hand['details']['dealt'] = 0
        for player in players:
            if players[player]['is_sitting'] == True:
                object_hand['details']['sitting'] += 1
                players[player]['result'] = 0
            else:
                object_hand['details']['dealt'] += 1
        object_hand['details']['players'] = players
        return True

    object_hand = {
        'error': { 'value': False, 'is_cancelled': False },
        'details': {}
    }
    re_lines = {
        'hand_and_date': r'^Hand #(\d+-\d+) - (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})',
        'game_and_stake': r'^Game: (.+) \(\d+\.?\d* - \d+\.?\d*\) - (Stakes|Blinds) (\d+\.?\d*)\/(\d+\.?\d*)( Ante (\d+\.?\d*))?',
        'table': r'^Table: (.+)',
        'cancelled': 'Hand cancelled',
        'rake_and_pot': r'^Rake \((\d+\.?\d*)\) Pot \((\d+\.?\d*)\)',
        'player_seating': r'^Seat (\d): (.*) \((\d+\.?\d*)\)( - sitting out)?',
        'player_result': r'^Seat \d+: (.*) \(([+|-]\d+\.?\d*)\) \[(.*)\] (.*)',
        'side_pot': r'^(.*) (wins|splits) (Hi |Lo )?Side Pot \d (.*)',
        'site': r'Site: (.*)',
        'board': r'Board: \[(.*)\], Players: .*',
    }

    if len(old_lines) < 4:
        object_hand['error']['value'] = True
        object_hand['error']['message'] = 'Improper Heading'
        return object_hand

    if bool(get_hand_and_date(object_hand, old_lines[0], re_lines['hand_and_date'])) == False:
        return object_hand
    if bool(get_game_and_stake(object_hand, old_lines[1], re_lines['game_and_stake'])) == False:
        return object_hand
    if bool(verify_mania(object_hand, old_lines[2], re_lines['site'])) == False:
        return object_hand
    if bool(get_table(object_hand, old_lines[3], re_lines['table'])) == False:
        return object_hand
    if bool(is_not_cancelled(object_hand, old_lines[4], re_lines['cancelled'])) == False:
        return object_hand
    if bool(get_rake_and_pot(object_hand, old_hand_text, re_lines['rake_and_pot'])) == False:
        return object_hand
    if bool(get_players(object_hand, old_hand_text, re_lines['player_seating'], re_lines['player_result'])) == False:
        return object_hand

    # keep track of side pots
    side_pot = re.search(re_lines['side_pot'], old_hand_text, re.M)
    object_hand['details']['has_side'] = bool(side_pot)
    # body starts from dealer button or posts
    lines_to_skip = 4 + int(object_hand['details']['dealt']) + int(object_hand['details']['sitting'])
    object_hand['details']['body'] = '\n'.join(body[lines_to_skip:])

    # for hem
    object_hand['details']['board'] = re.findall(re_lines['board'], old_hand_text, flags=re.M)

    return object_hand

def get_stats(hh_obj, details):
    games = hh_obj['games']
    players = hh_obj['players']

    if details['game'] not in games:
        games[details['game']] = True

    for player in details['players']:
        game = details['game']
        result = float(details['players'][player]['result'])

        if player not in players:
            players[player] = { 'games': {}, 'count': 0 }

        if game not in players[player]['games']:
            players[player]['games'][game] = {'amount': 0,'count': 0,'sit': 0}

        if details['players'][player]['is_sitting'] == True:
            players[player]['games'][game]['sit']+=1
        else:
            players[player]['count']+=1
            players[player]['games'][game]['count']+=1
            players[player]['games'][game]['amount']+=result
