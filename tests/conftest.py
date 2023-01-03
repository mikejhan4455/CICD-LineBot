import os
import sys

from FirebaseHandler import FirebaseHandler

sys.path.append("../")

import pytest
import dotenv
from linebot import LineBotApi
from MessageEventHandler import MessageEventHandler


@pytest.fixture(scope="module")
def channel_secret():
    dotenv.load_dotenv(".env.yaml")
    CHANNEL_SECRET = os.getenv("CHANNEL_SECRET", "")

    if CHANNEL_SECRET is None:
        raise Exception("LINE_CHANNEL_SECRET not defined")

    return CHANNEL_SECRET


@pytest.fixture(scope="module")
def channel_access_token():
    dotenv.load_dotenv(".env.yaml")
    CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "")

    if CHANNEL_ACCESS_TOKEN is None:
        raise Exception("LINE_CHANNEL_ACCESS_TOKEN not defined")

    return CHANNEL_ACCESS_TOKEN


@pytest.fixture(scope="module")
def line_bot_api():
    dotenv.load_dotenv(".env.yaml")
    return LineBotApi(channel_access_token)


@pytest.fixture(scope="module")
def message_event_handler():
    return MessageEventHandler()


@pytest.fixture(scope="module")
def firebase_handler():
    dotenv.load_dotenv(".env.yaml")
    FIREBASE_URL = os.getenv("FIREBASE_URL", "")

    if FIREBASE_URL is None:
        raise Exception("FIREBASE_URL not defined")


    return FirebaseHandler(FIREBASE_URL)





