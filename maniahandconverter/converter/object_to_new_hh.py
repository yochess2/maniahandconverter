import re

AVAILABLE_GAMES = {
    'LHE': "Limit Hold'em",
    'OMAHA': "Limit Omaha",
    'OMAHA8': "Limit Omaha Hi-Lo",
    'RAZZ': "Limit Razz",
    'STUD': "Limit Stud",
    'STUD8': "Limit Stud Hi-Lo",
    'PLO': "PL Omaha",
    'PLO8': "PL Omaha Hi-Lo",
    'NL': "NL Hold'em",
}

def init(hh_obj, heroname):
    result = {
      'supported_hands_array': [],
      'not_supported_hands_array': [],
      'has_side_array': []
    }

    for obj_details in hh_obj['hands']:
        hand_details = obj_details['details']
        if heroname not in hand_details['players']:
            continue
        if hand_details['players'][heroname]['is_sitting']:
            continue
        # need to work on this
        if hand_details['has_side']:
            message = 'Hand #' + hand_details['hand_number'] + ': Will do side pots later'
            result['has_side_array'].append(message)
            continue

        converted_hand = create_hand(heroname, hand_details)
        if converted_hand['supported'] == False:
            message = 'Hand #' + hand_details['hand_number'] + ': ' + \
                    hand_details['game'] + ' is currently not supported'
            result['not_supported_hands_array'].append(message)
        else:
            converted_hand_text = '\n'.join(converted_hand['lines'])
            result['supported_hands_array'].append(converted_hand_text)

    return result

# note: sitting and dealt are both numbers
# rest of numbers are in strings
def create_hand(heroname, hand_details):
    converted_hand = { 'error': False }

    if hand_details['game'] == AVAILABLE_GAMES['LHE']:
        game = "Hold'em Limit"
        converted_hand['supported'] = True
    elif hand_details['game'] == AVAILABLE_GAMES['NL']:
        game = "Hold'em No Limit"
        converted_hand['supported'] = True
    elif hand_details['game'] == AVAILABLE_GAMES['PLO']:
        game = "Omaha Pot Limit"
        converted_hand['supported'] = True
    elif hand_details['game'] == AVAILABLE_GAMES['OMAHA']:
        game = "Omaha Limit"
        converted_hand['supported'] = True
    elif hand_details['game'] == AVAILABLE_GAMES['OMAHA8']:
        game = "Omaha Hi/Lo Limit"
        converted_hand['supported'] = True
    elif hand_details['game'] == AVAILABLE_GAMES['PLO8']:
        game = "Omaha Hi/Lo Pot Limit"
        converted_hand['supported'] = True
    else:
        converted_hand['supported'] = False

    if converted_hand['supported'] == True:
        body = hand_details['body'].split('\n')
        if hand_details['blind_type'] == 'Blinds':
            bb = hand_details['bb']
        else:
            bb = '{:.2f}'.format(float(hand_details['bb']) / 2.0)

        holecard = hand_details['players'][heroname]['hole']
        button_num = get_button_num(hand_details['players'], body)
        heading_lines = get_heading_lines(hand_details, button_num, game)
        seating_lines = get_seating_lines(hand_details['players'])
        ante_lines, body_index = get_ante_lines(body, hand_details['ante'])
        blind_lines, body_index = get_blind_lines(body, body_index, hand_details)
        hole_lines, body_index = get_hole_lines(heroname, holecard, body_index)
        body_lines, body_index = get_body_lines(body, body_index, bb)
        summary_line = get_summary_line(body[-1])
        board_line = get_board_line(hand_details['board'])
        result_lines = get_result_lines(hand_details['players'])

        converted_hand['lines'] =   heading_lines + \
                                    seating_lines + \
                                    ante_lines    + \
                                    blind_lines   + \
                                    hole_lines    + \
                                    body_lines    + \
                                    summary_line  + \
                                    board_line    + \
                                    result_lines

    return converted_hand

def add_dollars(sb, bb):
    return '$' + sb + '/' + '$' + bb + ' USD'

def convert_date(date_str, time_str):
    return date_str.replace('-', '/') + ' ' + time_str + ' ET'

def get_button_num(players, body):
    button_line = body[0]
    name = button_line.split()[0]
    found = False
    button_num = None
    for player_name in players:
        if player_name == name:
            button_num = players[player_name]['seat']
    return button_num

def get_heading_lines(hand_details, button, game):
    result = []
    one = "PokerStars Hand #{}: {} ({}) - {}"
    result.append(one.format(
        hand_details['hand_number'],
        game,
        add_dollars(hand_details['sb'], hand_details['bb']),
        convert_date(hand_details['date'], hand_details['time'])
    ))
    two = "Table '{}' Seat #{} is the button"
    result.append(two.format(
        hand_details['table'],
        button
    ))
    return result

def get_seating_lines(players):
    result = []
    three = "Seat {}: {} (${:.2f} in chips)"
    for name in players:
        if players[name]['is_sitting'] == True:
            continue
        result.append(three.format(
            players[name]['seat'],
            name,
            float(players[name]['starting'])
        ))
    return result

def get_ante_lines(body, ante):
    result = []
    index = 1
    four = "{}: posts the ante ${:.2f}"
    hole_rx = r'^\*\* Hole Cards \*\* \[\d players\]'
    sb_rx = r'^.* posts small blind \d+'
    bb_rx = r'^.* posts big blind \d+'
    sb_bb_rx = r'(.*) posts (small \& big blind) (.*)'
    for line in body[1:]:
        if bool(re.search(sb_rx, line)) or bool(re.search(bb_rx, line)) or bool(re.search(hole_rx, line)):
            break
        elif bool(re.search(sb_bb_rx, line)):
            break
        name = line.split()[0]
        result.append(four.format(
            name,
            float(ante)
        ))
        index+=1
    return [result, index]

def get_blind_lines(body, body_index, hand_details):
    result = []
    index = body_index
    five = "{}: posts {} blind ${:.2f}"
    hole_rx = r'^\*\* Hole Cards \*\* \[\d players\]'
    sb_bb_rx = r'(.*) posts (small \& big blind) (.*)'
    for line in body[body_index:]:
        if bool(re.search(hole_rx, line)):
            break
        elif bool(re.search(sb_bb_rx, line)):
            name = line.split()[0]
            result.append(
                '{}: posts small blind ${:.2f} and big blind ${:.2f}'.format(
                name,
                float(hand_details['sb']),
                float(hand_details['bb'])
            )
        )
        else:
            blind_line = line.split()
            result.append(five.format(
                blind_line[0],
                blind_line[2],
                float(blind_line[4])
            )
        )
        index+=1
    return [result, index]

def get_hole_lines(heroname, holecard, body_index):
    result = ['*** HOLE CARDS ***']
    index = body_index + 1
    result.append(
        'Dealt to {} [{}]'.format(
        heroname,
        holecard
    ))
    return [result, index]

def get_body_lines(body, body_index, bb):
    result = []
    index = body_index
    action = "preflop"
    timed_rx = r'^(.*) has timed out'
    title_rx = r'^\*\* (.*) \*\* \[(.*)\]'
    last_num = bb
    for line in body[body_index:]:
        r = re.search(title_rx, line)
        if bool(re.search(timed_rx, line)):
            continue
        if bool(r):
            action = r.group(1)
            if action == "Flop":
                flop_cards = r.group(2)
                new_line = "*** FLOP *** [{}]".format(flop_cards)
            elif action == "Turn":
                turn_card = r.group(2)
                new_line = "*** TURN *** [{}] [{}]".format(flop_cards, turn_card)
            elif action == "River":
                river_card = r.group(2)
                new_line = "*** RIVER *** [{} {}] [{}]".format(flop_cards, turn_card, river_card)
            elif action == "Pot Show Down":
                new_line = "*** SHOW DOWN ***"
            else:
                print('unhandled line: ', line)
            result.append(new_line)
        else:
            r = re.search('^(.*) refunded (.*)', line)
            if bool(r):
                result.append("Uncalled bet (${}) returned to {}".format(r.group(2), r.group(1)))
                continue
            r = re.search(r'(.*) splits Pot \((.*)\) with (.*)', line)
            if bool(r):
                result.append("{} collected {} from pot".format(r.group(1), r.group(2)))
                continue
            r = re.search(r'(.*) wins Pot \((.*)\)', line)
            if bool(r):
                result.append("{} collected ${} from pot".format(r.group(1), r.group(2)))
                continue

            if action == "preflop" or action == "Flop" or action == "Turn" or action == "River":
                r = re.search(r'^(.*) folds', line)
                if bool(r):
                    result.append("{}: folds".format(r.group(1)))
                    continue
                r = re.search(r'^(.*) checks', line)
                if bool(r):
                    result.append("{}: checks".format(r.group(1)))
                    continue
                r = re.search(r'^(.*) calls (\d+\.*\d*)( \((All-in)\))?', line)
                if bool(r):
                    new_line = "{}: calls ${}".format(r.group(1), r.group(2))
                    if bool(r.group(3)):
                        new_line += " and is {}".format(r.group(4).lower())
                    result.append(new_line)
                    continue
                r = re.search(r'^(.*) bets (\d+\.*\d*)( \((All-in)\))?', line)
                if bool(r):
                    new_line = "{}: bets ${}".format(r.group(1), r.group(2))
                    if bool(r.group(3)):
                        new_line += " and is {}".format(r.group(4).lower())
                    last_num = r.group(2)
                    result.append(new_line)
                    continue
                r = re.search('^(.*) raises to (\d+\.*\d*)( \((All-in)\))?', line)
                if bool(r):
                    new_line = "{}: raises ${} to ${}".format(r.group(1), last_num, r.group(2))
                    if bool(r.group(3)):
                        new_line += " and is {}".format(r.group(4).lower())
                    last_num = r.group(2)
                    result.append(new_line)
                    continue
            elif action == "Pot Show Down":
                r = re.search(r'(.*) shows \[(.*)\] \((.*)\)', line)
                if bool(r):
                    result.append("{}: shows [{}] ({})".format(r.group(1), r.group(2), r.group(3)))
                    continue
            else:
                print('unhandled line: ', line)

    return [result, index]

def get_summary_line(line):
    result = []
    result.append("*** SUMMARY ***")
    r = re.search(r'^Rake \((\d+\.*\d*)\) Pot \((\d+\.*\d*)\) Players \(.*\)', line)
    if bool(r):
        result.append("Total pot ${} | Rake ${}".format(r.group(2), r.group(1)))

    return result

def get_board_line(board):
    b = ''.join(board)
    result = []
    result.append("Board [{}]".format(b))
    return result

def get_result_lines(players):
    results = []
    for name in players:
        player = players[name]
        if player['is_sitting']:
            continue
        if re.match(r'Folded on PreFlop', player['summary'].strip()):
            results.append("Seat {}: {} folded before Flop".format(player['seat'], name))

        elif re.match(r'Folded on Flop', player['summary'].strip()):
            results.append("Seat {}: {} folded on the Flop".format(player['seat'], name))

        elif re.match(r'Folded on Turn', player['summary'].strip()):
            results.append("Seat {}: {} folded on the Turn".format(player['seat'], name))

        elif re.match(r'Folded on River', player['summary'].strip()):
            results.append("Seat {}: {} folded on River".format(player['seat'], name))
        else:
            results.append("Seat {}: {} showed [{}] and {}".format(player['seat'], name, player['hole'], player['summary'].strip()))
    return results
