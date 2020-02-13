from django.http import HttpResponse
from django.http import JsonResponse
import os
import logging
import re
import random
import json
from utils.log import Logger
import utils.CQSDK as CQSDK
import time
from handler.command_dispatcher import CommandDispatcher


dispatcher = CommandDispatcher()


def marisa(request):

    logger = logging.getLogger(Logger.LOGGER_NAME)
    post = json.loads(request.body.decode('utf-8'))
    logger.debug("收到信息：" + str(post))
    message = post.get("message", "")
    send_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(post["time"]))
    message_type = post.get("message_type", "")
    self_qq = post.get("self_id", "")
    sender_qq = post["sender"]["user_id"]
    sender_name = post["sender"]["nickname"]
    if message_type == "group":
        group_id = post["group_id"]
        sender_card = post["sender"]["card"]
        OnEvent_GroupMsg(group_id=group_id, sender_id=sender_qq, sender_name=sender_card, msg=message)

    elif message_type == "private":
        OnEvent_PrivateMsg(fromQQ=sender_qq, msg=message)
    return JsonResponse({})


def OnEvent_PrivateMsg(fromQQ, msg):
    try:
        if dispatcher.is_command(msg):
            res = dispatcher.execute_cmd(msg, fromQQ, '0')

            if res is not None:
                logging.info(res)
                if isinstance(res, str):
                    CQSDK.send_private_msg(fromQQ, res)
                else:
                    CQSDK.send_private_msg(fromQQ, res[0])
    except Exception as e:
        logging.exception(e)


def OnEvent_GroupMsg(group_id, sender_id, sender_name, msg):
    try:
        if dispatcher.is_command(msg):
            res = dispatcher.execute_cmd(msg, sender_id, group_id)

            if res is not None:
                logging.info(res)
                if isinstance(res, str):
                    CQSDK.send_group_msg(group_id, res)
                else:
                    if res[1]:
                        CQSDK.send_private_msg(sender_id, res[0])
                        if res[2] is not None:
                            CQSDK.send_group_msg(group_id, res[2])
                    else:
                        CQSDK.send_group_msg(group_id, res[0])
    except Exception as e:
        logging.exception(e)
