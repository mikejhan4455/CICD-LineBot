import os
import requests
import json
import dotenv
from argparse import ArgumentParser


# laod environment variabels
dotenv.load_dotenv(".env.yaml")

# add argument parser
parser: ArgumentParser = ArgumentParser()
parser.add_argument("text", help="Text to send", type=str, default="")

args = parser.parse_args()


# main logic of sending message
headers = {
    "Authorization": "Bearer {}".format(os.getenv("CHANNEL_ACCESS_TOKEN")),
    "Content-Type": "application/json",
}
body = {
    "to": os.getenv("PERSONAL_USERID"),
    "messages": [{"type": "text", "text": args.text}],
}
# 向指定網址發送 request
req = requests.request(
    "POST",
    "https://api.line.me/v2/bot/message/push",
    headers=headers,
    data=json.dumps(body).encode("utf-8"),
)
# 印出得到的結果
print(req.text)
