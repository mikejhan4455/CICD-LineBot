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
from MessageEventHandler import MessageEventHandler

# Define global env and objects
dotenv.load_dotenv(".env.yaml")

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("CHANNEL_SECRET", "")
channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN", "")

if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    raise Exception("LINE_CHANNEL_SECRET not defined")

if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    raise Exception("LINE_CHANNEL_ACCESS_TOKEN not defined")


handler = WebhookHandler(channel_secret)
line_bot_api = LineBotApi(channel_access_token)
message_event_handler = MessageEventHandler()


@functions_framework.http
def callback(request):
    """HTTP Cloud Function. Main interface of requests"""

    # get X-Line-Signature header value
    signature_from_requests = request.headers["X-Line-Signature"]
    print(f"request.json: {request.json}")

    # # Compare x-line-signature request header and the signature
    # TODO: WIP
    # body = request.json
    # hash_value = hmac.new(
    #     channel_secret.encode("utf-8"), str(body).encode("utf-8"), hashlib.sha256
    # ).digest()

    # signature_from_requests = base64.b64encode(hash_value)

    # if signature_from_requests != hash_value:
    #     raise InvalidSignatureError

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
    print(f"type(event): {type(event)}")
    print(f"event: {event}")

    reply_messages = message_event_handler(event)

    line_bot_api.reply_message(
        event.reply_token, [TextSendMessage(text=message) for message in reply_messages]
    )
