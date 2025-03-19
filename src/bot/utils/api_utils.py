import datetime
import os

from bot import errors
from bot.definitions import APIS_PATH, ApiErrors

APIS = {}
API_INDEX = 0

def load_apis():
    global APIS
    if os.path.exists(APIS_PATH):
        with open(APIS_PATH, "r", encoding="utf-8") as f:
            loaded_apis = f.read().split("\n")
            for api in loaded_apis:
                if api not in APIS:
                    APIS[api] = {}

def api_error(api, api_error, wait_time=10):
    global APIS
    load_apis()
    if api in APIS:
        if api_error == ApiErrors.RATELIMIT:
            APIS[api]["wait_until"] = datetime.datetime.now() + datetime.timedelta(seconds=wait_time)
        elif api_error == ApiErrors.RESTRICTED:
            APIS[api]["banned"] = True


def get_api():
    global APIS, API_INDEX
    load_apis()

    api_list = []
    time_now = datetime.datetime.now()

    for api in APIS:
        if "banned" in APIS[api] and APIS[api]["banned"]:
            continue

        if "wait_until" in APIS[api]:
            if time_now > APIS[api]["wait_until"]:
                api_list.append(api)
        else:
            api_list.append(api)

    api_list = list(sorted(api_list, key=lambda api: APIS[api]["last_use_time"] if "last_use_time" in APIS[api] else 0))
    if len(api_list) == 0:
        raise errors.NoAvailableApis

    APIS[api_list[0]]["last_use_time"] = time_now.timestamp()
    return api_list[0]
