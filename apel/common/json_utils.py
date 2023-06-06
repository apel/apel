import json

JSON_MSG_BOILERPLATE = """{
    "Type": "%s",
    "Version": "%s",
    "UsageRecords": %s
}"""


def to_string(json_dict, dlm=''):
    """ Convert a dict into a valid json string """
    json_string = str(json_dict).replace("'", '"')

    try:
        json_dict_conv = json.loads(json_string)
    except json.decoder.JSONDecodeError:
        raise Exception('Unable to generate valid JSON. Make sure speech marks or apostrophes are escaped correctly.')

    if json_dict != json_dict_conv:
        raise Exception('JSON conversion unsuccessful because input dict does not match reconstructed dict.')

    return json_string

def to_dict(json_string):
    """ Convert a valid json string into a dict """

    try:
        json_dict = json.loads(json_string)
    except json.decoder.JSONDecodeError as e:
        print(e)
        raise Exception(e, '\n\nJSON string is not valid.')

def to_message(type, version, *usage_records):
    """ Generate JSON message format """
    return (JSON_MSG_BOILERPLATE % (type, version, list(usage_records))).replace("'", '"')
