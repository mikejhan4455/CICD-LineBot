import base64
import hashlib
import hmac
import os
import re
import sys
from datetime import datetime

import dotenv
import functions_framework
from firebase import firebase
from flask import abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# Define global env and objects
dotenv.load_dotenv(".env.yaml")
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))


@functions_framework.http
def callback(request):
    """HTTP Cloud Function. Main interface of requests"""

    # get channel_secret and channel_access_token from your environment variable
    channel_secret = os.getenv("CHANNEL_SECRET", None)
    channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN", None)
    if channel_secret is None:
        print("Specify LINE_CHANNEL_SECRET as environment variable.")
        sys.exit(1)
    if channel_access_token is None:
        print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
        sys.exit(1)

    # get X-Line-Signature header value
    signature_from_requests = request.headers["X-Line-Signature"]
    print(request.json)

    #  # Compare x-line-signature request header and the signature
    #  # TODO: Under development
    # body = request.json
    # hash_value = hmac.new(
    #     channel_secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    # ).digest()
    # signature_from_requests = base64.b64encode(hash_value)
    # print("signature_from_requests: {}".format(signature_from_requests))
    # print("signature_from_hash: {}".format(hash_value))

    # if signature_from_requests != hash_value:
    #     raise Exception
    # else:
    #     print("signature is the same")

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature_from_requests)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    """Handle All TextMessage from requesets of LINE."""

    user_id = event.source.user_id
    message = event.message.text

    # Add simple business logics
    INSTRUCTION = ["早安", "記住", "還原"]

    reply_text = ""

    if message.startswith(INSTRUCTION[0]):
        reply_text = datetime.today().strftime("%Y-%m-%d")

    elif message.startswith(INSTRUCTION[1]):
        word = event.message.text.replace(INSTRUCTION[1], "")
        firebase_handler("write", user_id=user_id, word=word)
        reply_text = "我已記住：{}".format(word)

    elif message.startswith(INSTRUCTION[2]):
        remember_words = firebase_handler("read", user_id)
        if remember_words:
            text = remember_words.pop()
            reply_text = "你要我記住: {}".format(text)
            firebase_handler("delete", user_id)

        else:
            reply_text = "沒有記住任何東西"

    else:
        reply_text = message

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))


def firebase_handler(action, user_id, word=None):
    # TODO: Add Auth step

    if action not in ["read", "write", "create", "delete"]:
        raise Exception()

    url = os.getenv("FIREBASE_URL")
    fb = firebase.FirebaseApplication(url, None)

    if action == "read":
        data = fb.get(url + "users/" + user_id, None)
        return data

    elif action == "write":
        user_data = firebase_handler("read", user_id)

        try:
            user_data["users"]["store_words"].append(word)
            fb.put(url, name="users", data=user_data)
        except:
            firebase_handler("create", user_id, word)

    elif action == "create":
        data = {user_id: {"words": [word]}}
        fb.put(url, name="users", data=data)

    elif action == "delete":
        user_data = firebase_handler("read", user_id)
        user_data["users"]["store_words"].pop()
        fb.put(url, name="users", data=user_data)
