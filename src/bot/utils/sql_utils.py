import json
import random
import string


def convert_to_sqlite_string(messages: list | dict):
    if type(messages) == dict:
        for key in messages:
            if type(messages[key]) != str:
                convert_to_sqlite_string(messages[key])
            else:
                messages[key] = messages[key].replace("'", "''")
    elif type(messages) == list:
        for i in range(len(messages)):
            if type(messages[i]) != str:
                convert_to_sqlite_string(messages[i])
            else:
                messages[i] = messages[i].replace("'", "''")

    return json.dumps(messages)

