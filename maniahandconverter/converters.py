from .converter import hh_to_object, object_to_new_hh
import tempfile, json

def create_hh_object(hh):
    hh_text = str(hh.file.read(), 'utf-8').strip()
    obj = hh_to_object.init(hh_text)
    return obj

def create_hh_details(hh_obj):
    unconvertable_hands = []
    convertable_hands = []
    for hand in hh_obj['unconvertable_hands']:
        message = "Hand #{}: {}".format(
            hand['details']['hand_number'],
            hand['error']['message']
        )
        unconvertable_hands.append(message)

    for hand in hh_obj['hands']:
        message = "Hand #{}: {}".format(
            hand['details']['hand_number'],
            hand['details']['game']
        )
        convertable_hands.append(message)

    return '\n'.join(unconvertable_hands + convertable_hands)

def parse_hh_json(file):
    byte_text = file.read()
    string = byte_text.decode('utf-8')
    hh_obj = json.loads(string)
    return hh_obj

def create_new_hh(hh_obj, hero):
    obj =  object_to_new_hh.init(hh_obj, hero)

    text = '\n'.join(obj['not_supported_hands_array']) + \
      '\n\n\n\n\n' + '\n'.join(obj['has_side_array']) + \
      '\n\n\n\n\n' + '\n\n'.join(obj['supported_hands_array'])

    return text
