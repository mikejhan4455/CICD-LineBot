import re
import functions_framework
import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)
import dotenv
import base64
import hashlib
import hmac
from datetime import datetime


dotenv.load_dotenv(".env.yaml")
line_bot_api = LineBotApi(os.getenv("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))


@functions_framework.http
def callback(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

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

    # Add simple business logics
    INSTRUCTION = ["早安", "記住", "還原"]
    remember_words = []
    reply_text = ""

    if INSTRUCTION[0] in event.message.text:
        reply_text = datetime.today().strftime("%Y-%m-%d")

    elif INSTRUCTION[1] in event.message.text:
        remember_words.append(event.message.text.split(" ")[-1])
        reply_text = "我已記住：{}".format(remember_words[-1])

    elif INSTRUCTION[3] in event.message.text:
        if len(remember_words):
            text = remember_words.pop()
            reply_text = "你要我記住: {}".format(text)

        else:
            reply_text = "沒有記住任何東西"

    else:
        reply_text = event.message.text

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
