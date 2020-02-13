import requests
import json
import os
import logging
import utils.log
import urllib.parse


url = ""
logger = logging.getLogger(utils.log.Logger.LOGGER_NAME)


def read_config_url():
    global url

    print(os.path.abspath(os.path.dirname(__file__)))
    if url != "":
        return url

    with open("config.json", 'r', encoding="utf-8") as f:
        content = json.load(f)
        url = content['coolq_server_url']
        return url


def execute_bak(cmd, json_obj):
    target_url = "{url}/{prefix}".format(url=read_config_url(), prefix=cmd)

    response = requests.post(target_url, data=str(json_obj), headers={"Encode": "UTF-8", "Content-Type": "application/json"})
    print(response.text)


def execute(cmd, json_obj):
    target_url = "{url}/{prefix}".format(url=read_config_url(), prefix=cmd)
    logger.info("Send get request to {}".format(target_url))
    response = requests.get(target_url, params=json_obj)
    print(response.text)


def send_private_msg(qq, msg):
    json_obj = {
        "user_id": qq,
        "message": msg
    }
    execute("send_private_msg", json_obj)


def send_group_msg(group_id, msg):
    json_obj = {
        "group_id": group_id,
        "message": msg
    }
    execute("send_group_msg", json_obj)
